#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <vector>
#include <omp.h>
using namespace std;using D=long double;
struct V{D x[3];D&operator[](int i){return x[i];}D operator[](int i)const{return x[i];}};
V sub(V a,V b){return{{a[0]-b[0],a[1]-b[1],a[2]-b[2]}};}D dot(V a,V b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}V cross(V a,V b){return{{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]}};}D cr(V a,V b,int x,int y){return a[x]*b[y]-a[y]*b[x];}
V readv(ifstream&f){double x[3];f.read((char*)x,24);return{{x[0],x[1],x[2]}};}
struct Tri{V a,e1,e2,n;int x,y;D det;};struct Query{V o,d;D a,b,c;int face,sample;};struct Bound{int tri,role;D lo,hi,plane,nd;};
int main(int argc,char**argv){ifstream tf(argv[1],ios::binary|ios::ate);int nf=tf.tellg()/72;tf.seekg(0);vector<Tri>ts;for(int i=0;i<nf;i++){V a=readv(tf),b=readv(tf),c=readv(tf);Tri t;t.a=a;t.e1=sub(b,a);t.e2=sub(c,a);t.n=cross(t.e1,t.e2);D len=sqrtl(dot(t.n,t.n));for(int k=0;k<3;k++)t.n[k]/=len;int ax=0;for(int k=1;k<3;k++)if(fabsl(t.n[k])>fabsl(t.n[ax]))ax=k;t.x=(ax+1)%3;t.y=(ax+2)%3;t.det=cr(t.e1,t.e2,t.x,t.y);ts.push_back(t);}
ifstream qf(argv[2],ios::binary|ios::ate);int nq=qf.tellg()/88;qf.seekg(0);vector<Query>qs(nq);for(auto&q:qs){q.o=readv(qf);q.d=readv(qf);double x[5];qf.read((char*)x,40);q.a=x[0];q.b=x[1];q.c=x[2];q.face=x[3];q.sample=x[4];}vector<vector<Bound>>out(nq);
#pragma omp parallel for schedule(dynamic,200)
for(int k=0;k<nq;k++){auto&q=qs[k];for(int f=0;f<nf;f++){auto&t=ts[f];D nd=dot(q.d,t.n);if(fabsl(nd)>=1e-12L)continue;V s=sub(q.o,t.a);D plane=dot(s,t.n);if(fabsl(plane)>=1e-10L)continue;D u=cr(s,t.e2,t.x,t.y)/t.det,v=cr(t.e1,s,t.x,t.y)/t.det,du=cr(q.d,t.e2,t.x,t.y)/t.det,dv=cr(t.e1,q.d,t.x,t.y)/t.det;D lo=0,hi=INFINITY;D val[3]={u,v,1-u-v},slope[3]={du,dv,-du-dv};for(int j=0;j<3;j++){if(fabsl(slope[j])<1e-27L){if(val[j]<-1e-15L)lo=INFINITY;}else if(slope[j]>0)lo=max(lo,-val[j]/slope[j]);else hi=min(hi,-val[j]/slope[j]);}for(int role=0;role<2;role++){D a=role?q.b:q.a,b=role?q.c:q.b;D aa=max(lo,a+1e-10L),bb=min(hi,b-1e-10L);if(bb-aa>1e-9L)out[k].push_back({f,role,aa,bb,plane,nd});}}}
ofstream of(argv[3]);of<<setprecision(21)<<"index,source_face,sample,boundary_face,role,start_t,end_t,plane_residual,normal_dot\n";size_t count=0;for(int k=0;k<nq;k++)for(auto&b:out[k]){of<<k<<','<<qs[k].face<<','<<qs[k].sample<<','<<b.tri<<','<<b.role<<','<<b.lo<<','<<b.hi<<','<<b.plane<<','<<b.nd<<'\n';count++;}cerr<<nq<<" queries, "<<nf<<" original triangles, "<<count<<" overlaps\n";}
