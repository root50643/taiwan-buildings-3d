// Direct BVH of the exact, unmodified original STL triangles.
// Generic predicates adapted from Shute strict_exact_source_intervals.cpp.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
using namespace std;
using D=long double;
struct V { D x[3]; D& operator[](int i){return x[i];} D operator[](int i)const{return x[i];} };
V operator+(V a,V b){return {{a[0]+b[0],a[1]+b[1],a[2]+b[2]}};}
V operator-(V a,V b){return {{a[0]-b[0],a[1]-b[1],a[2]-b[2]}};}
V operator*(V a,D b){return {{a[0]*b,a[1]*b,a[2]*b}};}
D dot(V a,V b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
V cross(V a,V b){return {{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]}};}
V norm(V a){return a*(1/sqrtl(dot(a,a)));}
struct Tri {V v[3],n,stored; bool valid=true;};
struct Node {V lo,hi;int a,b,l=-1,r=-1;};
struct Hit {D t,u,v,nd;int f;};
struct Boundary {D a,b,plane,nd;int f;};
struct Ray {vector<Hit> h;vector<Boundary>b;};
vector<Tri> T; vector<int> ids; vector<Node> N;
constexpr D EPS=1e-5L, MERGE=1e-10L;
const D W[10][3]={{1.L/3,1.L/3,1.L/3},{.98L,.01L,.01L},{.01L,.98L,.01L},{.01L,.01L,.98L},{.495L,.495L,.01L},{.01L,.495L,.495L},{.495L,.01L,.495L},{.49L,.49L,.02L},{.49L,.02L,.49L},{.02L,.49L,.49L}};
int build(int a,int b){
 Node n;n.a=a;n.b=b;n.lo={{INFINITY,INFINITY,INFINITY}};n.hi={{-INFINITY,-INFINITY,-INFINITY}};
 for(int k=a;k<b;k++)for(V v:T[ids[k]].v)for(int j=0;j<3;j++){n.lo[j]=min(n.lo[j],v[j]);n.hi[j]=max(n.hi[j],v[j]);}
 int q=N.size();N.push_back(n);
 if(b-a>8){int ax=0;for(int j=1;j<3;j++)if(n.hi[j]-n.lo[j]>n.hi[ax]-n.lo[ax])ax=j;int mid=(a+b)/2;
 nth_element(ids.begin()+a,ids.begin()+mid,ids.begin()+b,[ax](int i,int j){return T[i].v[0][ax]+T[i].v[1][ax]+T[i].v[2][ax]<T[j].v[0][ax]+T[j].v[1][ax]+T[j].v[2][ax];});
 int l=build(a,mid),r=build(mid,b);N[q].l=l;N[q].r=r;}return q;
}
bool box(const Node&n,V o,V d){D lo=0,hi=INFINITY;for(int j=0;j<3;j++){
 if(fabsl(d[j])<1e-27L){if(o[j]<n.lo[j]-1e-9L||o[j]>n.hi[j]+1e-9L)return false;}
 else {D a=(n.lo[j]-1e-9L-o[j])/d[j],b=(n.hi[j]+1e-9L-o[j])/d[j];if(a>b)swap(a,b);lo=max(lo,a);hi=min(hi,b);if(hi<lo)return false;}}return true;
}
D cr2(V a,V b,int x,int y){return a[x]*b[y]-a[y]*b[x];}
void scan(int k,V o,V d,Ray&r){const auto& node=N[k];if(!box(node,o,d))return;
 if(node.l>=0){scan(node.l,o,d,r);scan(node.r,o,d,r);return;}
 for(int j=node.a;j<node.b;j++){int fi=ids[j];const auto&t=T[fi];if(!t.valid)continue;
 V e1=t.v[1]-t.v[0],e2=t.v[2]-t.v[0],p=cross(d,e2),s=o-t.v[0];D det=dot(e1,p),dn=dot(d,t.n),plane=dot(s,t.n);
 if(fabsl(dn)<1e-12L&&fabsl(plane)<1e-10L){
  int ax=0;for(int x=1;x<3;x++)if(fabsl(t.n[x])>fabsl(t.n[ax]))ax=x;int x=(ax+1)%3,y=(ax+2)%3;
  D den=cr2(e1,e2,x,y),u=cr2(s,e2,x,y)/den,v=cr2(e1,s,x,y)/den,du=cr2(d,e2,x,y)/den,dv=cr2(e1,d,x,y)/den;
  D lo=0,hi=INFINITY;D val[3]={u,v,1-u-v},slope[3]={du,dv,-du-dv};
  for(int z=0;z<3;z++){if(fabsl(slope[z])<1e-27L){if(val[z]<-1e-15L)lo=INFINITY;}else if(slope[z]>0)lo=max(lo,-val[z]/slope[z]);else hi=min(hi,-val[z]/slope[z]);}
  if(hi>lo)r.b.push_back({lo,hi,plane,dn,fi});
 }
 if(det==0)continue;D u=dot(s,p)/det;if(u< -1e-15L||u>1+1e-15L)continue;V q=cross(s,e1);D v=dot(d,q)/det;
 if(v< -1e-15L||u+v>1+1e-15L)continue;D z=dot(e2,q)/det;if(z>0)r.h.push_back({z,u,v,dn,fi});
 }
}
Ray ray(V o,V d){Ray r;scan(0,o,d,r);sort(r.h.begin(),r.h.end(),[](const Hit&a,const Hit&b){return a.t==b.t?a.f<b.f:a.t<b.t;});sort(r.b.begin(),r.b.end(),[](const Boundary&a,const Boundary&b){return a.a==b.a?a.f<b.f:a.a<b.a;});return r;}
vector<D> unique_t(const Ray&r){vector<D> u;for(const auto&h:r.h)if(u.empty()||h.t-u.back()>MERGE)u.push_back(h.t);return u;}
// Independent oblique parity screen. Ambiguous/tangent events never silently count as a crossing.
int material(V p,int direction){
 V d=direction?norm(V{{.239117L,-.847313L,.474991L}}):norm(V{{.713123L,.431977L,.552111L}});auto r=ray(p,d);
 if(!r.b.empty())return -1;auto u=unique_t(r);int k=0,parity=0;
 for(D t:u){bool pos=false,neg=false;while(k<(int)r.h.size()&&fabsl(r.h[k].t-t)<=MERGE){D nd=r.h[k++].nd;if(fabsl(nd)<1e-12L)return -1;pos|=nd>0;neg|=nd<0;}
 if(pos&&neg)return -1;parity^=1;}return parity;
}
V readv(ifstream&f){double x[3];f.read((char*)x,24);if(!f)throw runtime_error("short binary input");return {{x[0],x[1],x[2]}};}
void printv(ostream&o,V p){for(D x:p.x)o<<','<<x;}
int main(int argc,char**argv){try{
 if(argc<4){cerr<<"usage: dense_original triangles_f64.bin stored_normals_f64.bin events.txt [face_limit] [stored|geometric]\n";return 2;}
 ifstream f(argv[1],ios::binary|ios::ate);if(!f)throw runtime_error("missing triangles");auto bytes=f.tellg();if(bytes<=0||bytes%72)throw runtime_error("bad triangle byte count");int nf=bytes/72;f.seekg(0);
 ifstream sn(argv[2],ios::binary|ios::ate);if(!sn||sn.tellg()!=nf*24)throw runtime_error("bad stored normal count");sn.seekg(0);T.resize(nf);
 for(auto&t:T){for(auto&v:t.v)v=readv(f);t.stored=readv(sn);V n=cross(t.v[1]-t.v[0],t.v[2]-t.v[0]);D l=sqrtl(dot(n,n));t.valid=isfinite(l)&&l>0;t.n=t.valid?n*(1/l):V{{NAN,NAN,NAN}};}
 for(int i=0;i<nf;i++)ids.push_back(i);build(0,nf);int limit=argc>4?min(nf,stoi(argv[4])):nf;bool stored=argc>5&&string(argv[5])=="stored";
 ofstream out(argv[3]);if(!out)throw runtime_error("cannot create output");out<<setprecision(21);
 // face,sample,source xyz,normal xyz,source_normal_valid,ten parity controls | hits | coplanar intervals
 for(int i=0;i<limit;i++){for(int s=0;s<10;s++){
  const auto&t=T[i];V n=stored?norm(t.stored):t.n,p={{0,0,0}};for(int j=0;j<3;j++)p=p+t.v[j]*W[s][j];
  bool valid=t.valid&&isfinite(dot(n,n))&&dot(n,t.n)>0;V o=p+n*EPS,d=n*-1;Ray r;if(valid)r=ray(o,d);auto u=unique_t(r);
  out<<i<<','<<s;printv(out,p);printv(out,n);out<<','<<valid;
  vector<V> ps;
  if(u.size()>=2&&u[1]>u[0]){D a=u[0],b=u[1],gap=u.size()>2?u[2]-b:1.L;
   ps={o+d*(a-min(EPS,a/2)),o+d*(a+min(EPS,(b-a)/4)),o+d*((a+b)/2),o+d*(b+min(EPS,gap/4)),o+d*(b+gap/2)};}
  for(int j=0;j<5;j++)for(int k=0;k<2;k++)out<<','<<(ps.empty()?-1:material(ps[j],k));
  out<<'|';for(const auto&h:r.h)out<<h.t<<','<<h.f<<','<<h.u<<','<<h.v<<','<<h.nd<<';';
  out<<'|';for(const auto&b:r.b)out<<b.a<<','<<b.b<<','<<b.f<<','<<b.plane<<','<<b.nd<<';';out<<'\n';
 }
 if(i%5000==0){out.flush();cerr<<i<<'/'<<limit<<" faces\n";}}
 cerr<<limit*10<<" complete dense rays\n";return out?0:2;
 }catch(const exception&e){cerr<<e.what()<<'\n';return 2;}}
