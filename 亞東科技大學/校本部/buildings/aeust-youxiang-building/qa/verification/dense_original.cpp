// Original-face BVH rays. Input is raw STL coordinates promoted to float64,
// in original face order. Every raw triangle hit is retained in the CSV.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <vector>
using namespace std;
using Real = long double;
struct Vec {
    Real v[3];
    Real& operator[](int i) { return v[i]; }
    Real operator[](int i) const { return v[i]; }
};
Vec operator+(Vec a, Vec b) { return {{a[0]+b[0], a[1]+b[1], a[2]+b[2]}}; }
Vec operator-(Vec a, Vec b) { return {{a[0]-b[0], a[1]-b[1], a[2]-b[2]}}; }
Vec operator*(Vec a, Real b) { return {{a[0]*b, a[1]*b, a[2]*b}}; }
Real dot(Vec a, Vec b) { return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
Vec cross(Vec a, Vec b) { return {{a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]}}; }
Real norm(Vec a) { return sqrtl(dot(a,a)); }
struct Triangle { Vec p[3]; Vec normal; };
struct Node { Vec low, high; int begin, end, left=-1, right=-1; };
struct Hit { Real t; int face, direction; };
struct Event { Real t; vector<Hit> members; int direction; bool ambiguous; };
struct Ray { vector<Hit> raw; vector<Event> events; bool ambiguous=false; };
vector<Triangle> triangles;
vector<int> ids;
vector<Node> nodes;
constexpr Real offset = 1e-5L;
constexpr Real cluster_tolerance = 1e-9L;
constexpr Real cluster_spread_limit = 1e-11L;

int build(int begin, int end) {
    Node node;
    node.begin=begin; node.end=end;
    node.low={{1e100L,1e100L,1e100L}};
    node.high={{-1e100L,-1e100L,-1e100L}};
    for (int k=begin;k<end;k++) for (Vec p:triangles[ids[k]].p)
        for (int axis=0;axis<3;axis++) {
            node.low[axis]=min(node.low[axis],p[axis]);
            node.high[axis]=max(node.high[axis],p[axis]);
        }
    int result=static_cast<int>(nodes.size()); nodes.push_back(node);
    if (end-begin>8) {
        int axis=0;
        for (int j=1;j<3;j++) if(node.high[j]-node.low[j]>node.high[axis]-node.low[axis]) axis=j;
        int middle=(begin+end)/2;
        nth_element(ids.begin()+begin,ids.begin()+middle,ids.begin()+end,[axis](int i,int j) {
            Real a=0,b=0;
            for(int k=0;k<3;k++) { a+=triangles[i].p[k][axis]; b+=triangles[j].p[k][axis]; }
            return a==b ? i<j : a<b;
        });
        int left=build(begin,middle), right=build(middle,end);
        nodes[result].left=left; nodes[result].right=right;
    }
    return result;
}

bool box_hit(const Node& node,Vec origin,Vec direction) {
    Real low=0,high=1e100L;
    for(int axis=0;axis<3;axis++) {
        if(fabsl(direction[axis])<1e-24L) {
            if(origin[axis]<node.low[axis]-1e-10L || origin[axis]>node.high[axis]+1e-10L) return false;
        } else {
            Real a=(node.low[axis]-1e-10L-origin[axis])/direction[axis];
            Real b=(node.high[axis]+1e-10L-origin[axis])/direction[axis];
            if(a>b) swap(a,b);
            low=max(low,a); high=min(high,b);
            if(high<low) return false;
        }
    }
    return true;
}

void scan(int index,Vec origin,Vec direction,vector<Hit>& hits) {
    const Node& node=nodes[index];
    if(!box_hit(node,origin,direction)) return;
    if(node.left>=0) {
        scan(node.left,origin,direction,hits); scan(node.right,origin,direction,hits); return;
    }
    for(int j=node.begin;j<node.end;j++) {
        int face=ids[j]; const Triangle& triangle=triangles[face];
        Vec edge1=triangle.p[1]-triangle.p[0],edge2=triangle.p[2]-triangle.p[0];
        Vec perpendicular=cross(direction,edge2);
        Real determinant=dot(edge1,perpendicular),scale=norm(cross(edge1,edge2));
        if(fabsl(determinant)<=scale*1e-15L) continue;
        Vec relative=origin-triangle.p[0];
        Real u=dot(relative,perpendicular)/determinant;
        if(u < -1e-12L || u > 1+1e-12L) continue;
        Vec q=cross(relative,edge1);
        Real v=dot(direction,q)/determinant;
        if(v < -1e-12L || u+v > 1+1e-12L) continue;
        Real distance=dot(edge2,q)/determinant;
        if(distance > 1e-12L) hits.push_back({distance,face,dot(direction,triangle.normal)>0 ? 1:-1});
    }
}

Ray cast(Vec origin,Vec direction) {
    Ray ray;
    scan(0,origin,direction,ray.raw);
    sort(ray.raw.begin(),ray.raw.end(),[](const Hit&a,const Hit&b) { return a.t==b.t ? a.face<b.face:a.t<b.t; });
    for(const Hit& hit:ray.raw) {
        if(ray.events.empty() || hit.t-ray.events.back().t>cluster_tolerance)
            ray.events.push_back({hit.t,{hit},hit.direction,false});
        else {
            Event& event=ray.events.back(); event.members.push_back(hit);
            // A cluster is only a shared-edge numerical coincidence, never a
            // license to merge distinct near surfaces or opposite crossings.
            if(hit.direction!=event.direction || hit.t-event.t>cluster_spread_limit) event.ambiguous=true;
        }
    }
    for(const Event& event:ray.events) if(event.ambiguous) ray.ambiguous=true;
    return ray;
}

int parity(Vec point) {
    Vec direction={{.713123L,.431977L,.552111L}};
    direction=direction*(1/norm(direction));
    Ray ray=cast(point,direction);
    if(ray.ambiguous) return -1;
    return static_cast<int>(ray.events.size()%2);
}

int main(int argc,char** argv) {
    try {
        if(argc!=3) throw runtime_error("Usage: dense_original triangles_float64.bin output.csv");
        ifstream input(argv[1],ios::binary|ios::ate);
        if(!input) throw runtime_error("Cannot read original triangle coordinate input");
        streamoff bytes=input.tellg();
        if(bytes<=0 || bytes%72!=0) throw runtime_error("Triangle input length is invalid");
        const int count=static_cast<int>(bytes/72); input.seekg(0);
        triangles.resize(count); ids.resize(count); iota(ids.begin(),ids.end(),0);
        for(Triangle& triangle:triangles) {
            double values[9]; input.read(reinterpret_cast<char*>(values),sizeof(values));
            if(!input) throw runtime_error("Truncated triangle input");
            for(int point=0;point<3;point++) for(int axis=0;axis<3;axis++) {
                if(!isfinite(values[point*3+axis])) throw runtime_error("Nonfinite original vertex");
                triangle.p[point][axis]=values[point*3+axis];
            }
            Vec normal=cross(triangle.p[1]-triangle.p[0],triangle.p[2]-triangle.p[0]);
            if(!(norm(normal)>0)) throw runtime_error("Degenerate original face");
            triangle.normal=normal*(1/norm(normal));
        }
        build(0,count);
        ofstream out(argv[2]);
        if(!out) throw runtime_error("Cannot create dense CSV");
        out<<setprecision(20);
        out<<"face,sample,x,y,z,nx,ny,nz,origin_x,origin_y,origin_z,entry,exit,first_solid,air_after,exit_x,exit_y,exit_z,inside_control,outside_control,mid_control,after_exit_control,source_face_in_entry,alternating_crossings,ambiguous_events,raw_hit_count,event_count,raw_intersections_t_face_direction,events_t_direction,paired_intervals,x_hex,y_hex,z_hex,nx_hex,ny_hex,nz_hex,origin_x_hex,origin_y_hex,origin_z_hex,dx_hex,dy_hex,dz_hex\n";
        const Real weights[10][3]={{1.L/3,1.L/3,1.L/3},{.98L,.01L,.01L},{.01L,.98L,.01L},{.01L,.01L,.98L},
            {.495L,.495L,.01L},{.01L,.495L,.495L},{.495L,.01L,.495L},
            {.49L,.49L,.02L},{.49L,.02L,.49L},{.02L,.49L,.49L}};
        for(int sample=0;sample<10;sample++) {
            for(int face=0;face<count;face++) {
                const Triangle& triangle=triangles[face]; Vec normal=triangle.normal;
                Vec point=triangle.p[0]*weights[sample][0]+triangle.p[1]*weights[sample][1]+triangle.p[2]*weights[sample][2];
                Vec origin=point+normal*offset,direction=normal*-1;
                Ray ray=cast(origin,direction);
                Real entry=ray.events.empty()?NAN:ray.events[0].t;
                Real finish=ray.events.size()<2?NAN:ray.events[1].t;
                Real next=ray.events.size()<3?INFINITY:ray.events[2].t;
                Vec exit_point=origin+direction*finish;
                bool source=false,alternating=!ray.events.empty() && ray.events.size()%2==0;
                if(!ray.events.empty()) for(const Hit& hit:ray.events[0].members) if(hit.face==face) source=true;
                for(size_t i=0;i<ray.events.size();i++) if(ray.events[i].direction!=(i%2==0?-1:1)) alternating=false;
                int inside=-1,outside=-1,middle=-1,after=-1;
                if(isfinite(entry)&&isfinite(finish)&&finish>entry) {
                    inside=parity(point-normal*min(offset,(finish-entry)/4));
                    outside=parity(origin);
                    middle=parity(origin+direction*((entry+finish)/2));
                    after=parity(exit_point+direction*min(offset,(next-finish)/4));
                }
                out<<face<<','<<sample;
                for(Real value:point.v) out<<','<<value;
                for(Real value:normal.v) out<<','<<value;
                for(Real value:origin.v) out<<','<<value;
                out<<','<<entry<<','<<finish<<','<<finish-entry<<','<<next-finish;
                for(Real value:exit_point.v) out<<','<<value;
                out<<','<<inside<<','<<outside<<','<<middle<<','<<after<<','<<source<<','<<alternating<<','<<ray.ambiguous<<','<<ray.raw.size()<<','<<ray.events.size()<<',';
                for(const Hit& hit:ray.raw) out<<hit.t<<':'<<hit.face<<':'<<hit.direction<<';';
                out<<',';
                for(const Event& event:ray.events) out<<event.t<<':'<<event.direction<<';';
                out<<',';
                for(size_t i=0;i+1<ray.events.size();i+=2) out<<ray.events[i].t<<':'<<ray.events[i+1].t<<';';
                // Preserve the exact long-double values from this execution for
                // independent rational diagnosis. No ray or acceptance logic changes.
                out<<hexfloat;
                for(Real value:point.v) out<<','<<value;
                for(Real value:normal.v) out<<','<<value;
                for(Real value:origin.v) out<<','<<value;
                for(Real value:direction.v) out<<','<<value;
                out<<defaultfloat<<setprecision(20);
                out<<'\n';
            }
            out.flush();
            if(!out) throw runtime_error("Dense CSV write failed");
            cerr<<"Sample "<<sample<<" complete: "<<(sample+1)*count<<" original-face rays\n";
        }
        return 0;
    } catch(const exception& error) {
        cerr<<error.what()<<'\n'; return 2;
    }
}
