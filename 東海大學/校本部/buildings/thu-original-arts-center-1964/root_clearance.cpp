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
  if(hi-lo>1e-10L)r.b.push_back({lo,hi,plane,dn,fi});
 }
 if(fabsl(det)<1e-27L)continue;D u=dot(s,p)/det;if(u< -1e-15L||u>1+1e-15L)continue;V q=cross(s,e1);D v=dot(d,q)/det;
 if(v< -1e-15L||u+v>1+1e-15L)continue;D z=dot(e2,q)/det;if(z>1e-12L)r.h.push_back({z,u,v,dn,fi});
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

D distance2(V p,V a){V x=p-a;return dot(x,x);}
V closest_segment(V p,V a,V b){V v=b-a;D den=dot(v,v);if(den<=0)return a;D f=dot(p-a,v)/den;return a+v*max(0.L,min(1.L,f));}
V closest_triangle(V p,const Tri&t){
 V a=t.v[0],b=t.v[1],c=t.v[2],ab=b-a,ac=c-a,ap=p-a;
 D d1=dot(ab,ap),d2=dot(ac,ap);if(d1<=0&&d2<=0)return a;
 V bp=p-b;D d3=dot(ab,bp),d4=dot(ac,bp);if(d3>=0&&d4<=d3)return b;
 D vc=d1*d4-d3*d2;if(vc<=0&&d1>=0&&d3<=0)return a+ab*(d1/(d1-d3));
 V cp=p-c;D d5=dot(ab,cp),d6=dot(ac,cp);if(d6>=0&&d5<=d6)return c;
 D vb=d5*d2-d1*d6;if(vb<=0&&d2>=0&&d6<=0)return a+ac*(d2/(d2-d6));
 D va=d3*d6-d5*d4;if(va<=0&&(d4-d3)>=0&&(d5-d6)>=0)return b+(c-b)*((d4-d3)/((d4-d3)+(d5-d6)));
 D den=va+vb+vc;if(den>0)return a+ab*(vb/den)+ac*(vc/den);
 V q=closest_segment(p,a,b);for(auto e:vector<pair<V,V>>{{b,c},{c,a}}){V r=closest_segment(p,e.first,e.second);if(distance2(p,r)<distance2(p,q))q=r;}return q;
}
D box_distance2(V p,const Node&n){D sum=0;for(int j=0;j<3;j++){D x=max(max(n.lo[j]-p[j],p[j]-n.hi[j]),0.L);sum+=x*x;}return sum;}
void nearest(int k,V p,D&best,int&face,V&at){const auto&n=N[k];if(box_distance2(p,n)>best)return;
 if(n.l>=0){D dl=box_distance2(p,N[n.l]),dr=box_distance2(p,N[n.r]);if(dl<=dr){nearest(n.l,p,best,face,at);nearest(n.r,p,best,face,at);}else{nearest(n.r,p,best,face,at);nearest(n.l,p,best,face,at);}return;}
 for(int j=n.a;j<n.b;j++){int fi=ids[j];V q=closest_triangle(p,T[fi]);D x=distance2(p,q);if(x<best){best=x;face=fi;at=q;}}
}
int main(int argc,char**argv){try{
 if(argc!=4)return 2;ifstream f(argv[1],ios::binary|ios::ate);if(!f)throw runtime_error("missing triangles");auto bytes=f.tellg();if(bytes<=0||bytes%72)throw runtime_error("bad triangle bytes");int nf=bytes/72;f.seekg(0);T.resize(nf);
 for(auto&t:T){for(auto&v:t.v)v=readv(f);V n=cross(t.v[1]-t.v[0],t.v[2]-t.v[0]);D l=sqrtl(dot(n,n));if(!(l>0))throw runtime_error("invalid source triangle");t.n=n*(1/l);}
 for(int i=0;i<nf;i++)ids.push_back(i);build(0,nf);ifstream q(argv[2],ios::binary|ios::ate);if(!q||q.tellg()%24)throw runtime_error("bad points");int nq=q.tellg()/24;q.seekg(0);ofstream out(argv[3]);out<<setprecision(21);
 for(int i=0;i<nq;i++){V p=readv(q),at;D best=INFINITY;int fi=-1;nearest(0,p,best,fi,at);out<<i<<','<<sqrtl(best)<<','<<fi;printv(out,at);out<<'\n';}return out?0:2;
 }catch(const exception&e){cerr<<e.what()<<'\n';return 2;}}
