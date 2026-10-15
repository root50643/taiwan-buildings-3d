#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <vector>
#include <iomanip>
using namespace std;
struct V{double x[3];double& operator[](int i){return x[i];} double operator[](int i)const{return x[i];}};
V operator+(V a,V b){return {{a[0]+b[0],a[1]+b[1],a[2]+b[2]}};}V operator-(V a,V b){return {{a[0]-b[0],a[1]-b[1],a[2]-b[2]}};}V operator*(V a,double s){return {{a[0]*s,a[1]*s,a[2]*s}};}double dot(V a,V b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}V cross(V a,V b){return {{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]}};}
struct Tri{V v[3];};struct Node{V lo,hi;int a,b,l=-1,r=-1;};vector<Tri>T;vector<int>ids;vector<Node>N;
int build(int a,int b){Node n;n.a=a;n.b=b;n.lo={{1e99,1e99,1e99}};n.hi={{-1e99,-1e99,-1e99}};for(int k=a;k<b;k++)for(V v:T[ids[k]].v)for(int j=0;j<3;j++){n.lo[j]=min(n.lo[j],v[j]);n.hi[j]=max(n.hi[j],v[j]);}int q=N.size();N.push_back(n);if(b-a>8){int ax=0;for(int j=1;j<3;j++)if(n.hi[j]-n.lo[j]>n.hi[ax]-n.lo[ax])ax=j;int mid=(a+b)/2;nth_element(ids.begin()+a,ids.begin()+mid,ids.begin()+b,[ax](int i,int j){return T[i].v[0][ax]+T[i].v[1][ax]+T[i].v[2][ax]<T[j].v[0][ax]+T[j].v[1][ax]+T[j].v[2][ax];});int l=build(a,mid),r=build(mid,b);N[q].l=l;N[q].r=r;}return q;}
bool box(Node& n,V o,V d){double mn=0,mx=1e99;for(int j=0;j<3;j++){if(abs(d[j])<1e-16){if(o[j]<n.lo[j]-1e-8||o[j]>n.hi[j]+1e-8)return false;}else{double a=(n.lo[j]-1e-8-o[j])/d[j],b=(n.hi[j]+1e-8-o[j])/d[j];if(a>b)swap(a,b);mn=max(mn,a);mx=min(mx,b);if(mx<mn)return false;}}return true;}
void scan(int k,V o,V d,vector<double>&h){Node&n=N[k];if(!box(n,o,d))return;if(n.l>=0){scan(n.l,o,d,h);scan(n.r,o,d,h);return;}for(int j=n.a;j<n.b;j++){Tri&t=T[ids[j]];V e1=t.v[1]-t.v[0],e2=t.v[2]-t.v[0],p=cross(d,e2);double det=dot(e1,p);if(abs(det)<1e-13)continue;V s=o-t.v[0];double u=dot(s,p)/det;if(u< -1e-9||u>1+1e-9)continue;V q=cross(s,e1);double v=dot(d,q)/det;if(v< -1e-9||u+v>1+1e-9)continue;double z=dot(e2,q)/det;if(z>1e-9)h.push_back(z);}}
vector<double> ray(V o,V d){vector<double>h;scan(0,o,d,h);sort(h.begin(),h.end());vector<double>u;for(double x:h)if(u.empty()||x-u.back()>1e-7)u.push_back(x);return u;}
bool inside(V p){V d={{.713123,.431977,.552111}};return ray(p,d).size()%2;}

struct Hit{double t;int f;};
void scanid(int k,V o,V d,vector<Hit>&h){Node&n=N[k];if(!box(n,o,d))return;if(n.l>=0){scanid(n.l,o,d,h);scanid(n.r,o,d,h);return;}for(int j=n.a;j<n.b;j++){int fi=ids[j];Tri&t=T[fi];V e1=t.v[1]-t.v[0],e2=t.v[2]-t.v[0],p=cross(d,e2);double det=dot(e1,p);if(abs(det)<1e-13)continue;V ss=o-t.v[0];double u=dot(ss,p)/det;if(u< -1e-12||u>1+1e-12)continue;V q=cross(ss,e1);double v=dot(d,q)/det;if(v< -1e-12||u+v>1+1e-12)continue;double z=dot(e2,q)/det;if(z>1e-9)h.push_back({z,fi});}}
vector<Hit> rayid(V o,V d){vector<Hit>h;scanid(0,o,d,h);sort(h.begin(),h.end(),[](Hit a,Hit b){return a.t<b.t;});vector<Hit>u;for(auto x:h)if(u.empty()||x.t-u.back().t>1e-7)u.push_back(x);return u;}
V normal(int i){auto t=T[i];auto n=cross(t.v[1]-t.v[0],t.v[2]-t.v[0]);return n*(1/sqrt(dot(n,n)));}
int controls(V p,V d){int a=0;for(double s:{.00001,.001,.01,.05})if(inside(p+d*s))a++;return a;}
int main(int argc,char**argv){ifstream f(argv[1],ios::binary|ios::ate);int nf=f.tellg()/sizeof(Tri);f.seekg(0);T.resize(nf);f.read((char*)T.data(),nf*sizeof(Tri));for(int i=0;i<nf;i++)ids.push_back(i);build(0,nf);ifstream q(argv[2]);ofstream out(argv[3]);out<<setprecision(15)<<"face,sample,x,y,z,raw_first,raw_air,strict_first,exit_face,pair_root,pair_exit,pair_inside,pair_maxdot,triple_root,triple_exit,triple_inside,triple_maxdot,dx,dy,dz,classification\n";int fi,sm;V p;double rf,ra;while(q>>fi>>sm>>p[0]>>p[1]>>p[2]>>rf>>ra){V n=normal(fi);auto h=rayid(p+n*1e-5,n*-1);if(h.size()<2)continue;int ex=h[1].f;double sf=h[1].t-h[0].t;V n1=normal(ex),d=(n+n1)*-1;double dr=sqrt(dot(d,d));double pr=-1,tr=-1,pdot=1,tdot=1;int pe=-1,te=-1,pc=0,tc=0;string cl="unresolved";
if(dr>1e-8){d=d*(1/dr);pdot=max(dot(d,n),dot(d,n1));auto ph=rayid(p+d*1e-5,d);if(!ph.empty()){pr=ph[0].t+1e-5;pe=ph[0].f;pc=controls(p,d);if(pr>=.8&&pc==4&&pdot< -1e-5)cl="two_actual_faces";else{V n2=normal(pe);V dd=(n+n1+n2)*-1;double dl=sqrt(dot(dd,dd));if(dl>1e-8){dd=dd*(1/dl);tdot=max({dot(dd,n),dot(dd,n1),dot(dd,n2)});auto th=rayid(p+dd*1e-5,dd);if(!th.empty()){tr=th[0].t+1e-5;te=th[0].f;tc=controls(p,dd);if(tr>=.8&&tc==4&&tdot< -1e-5){cl="three_actual_faces";d=dd;}}}}}}
if(sf>=.8)cl="strict_original_normal_long";
out<<fi<<','<<sm<<','<<p[0]<<','<<p[1]<<','<<p[2]<<','<<rf<<','<<ra<<','<<sf<<','<<ex<<','<<pr<<','<<pe<<','<<pc<<','<<pdot<<','<<tr<<','<<te<<','<<tc<<','<<tdot<<','<<d[0]<<','<<d[1]<<','<<d[2]<<','<<cl<<'\n';}}
