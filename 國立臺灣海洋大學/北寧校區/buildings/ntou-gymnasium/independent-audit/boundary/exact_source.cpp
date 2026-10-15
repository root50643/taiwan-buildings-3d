#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <vector>
#include <iomanip>
using namespace std;using D=long double;
struct V{D x[3];D&operator[](int i){return x[i];}D operator[](int i)const{return x[i];}};
V operator+(V a,V b){return{{a[0]+b[0],a[1]+b[1],a[2]+b[2]}};}V operator-(V a,V b){return{{a[0]-b[0],a[1]-b[1],a[2]-b[2]}};}V operator*(V a,D s){return{{a[0]*s,a[1]*s,a[2]*s}};}D dot(V a,V b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}V cross(V a,V b){return{{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]}};}V norm(V a){return a*(1/sqrtl(dot(a,a)));}
struct Tri{V v[3],n;};struct Node{V lo,hi;int a,b,l=-1,r=-1;};vector<Tri>T;vector<int>ids;vector<Node>N;struct Hit{D t,u,v,nd;int f;};struct Bound{D a,b,plane,nd;int f;};struct Ray{vector<Hit>h;vector<Bound>b;};
int build(int a,int b){Node n;n.a=a;n.b=b;n.lo={{1e99L,1e99L,1e99L}};n.hi={{-1e99L,-1e99L,-1e99L}};for(int k=a;k<b;k++)for(V v:T[ids[k]].v)for(int j=0;j<3;j++){n.lo[j]=min(n.lo[j],v[j]);n.hi[j]=max(n.hi[j],v[j]);}int q=N.size();N.push_back(n);if(b-a>8){int ax=0;for(int j=1;j<3;j++)if(n.hi[j]-n.lo[j]>n.hi[ax]-n.lo[ax])ax=j;int mid=(a+b)/2;nth_element(ids.begin()+a,ids.begin()+mid,ids.begin()+b,[ax](int i,int j){return T[i].v[0][ax]+T[i].v[1][ax]+T[i].v[2][ax]<T[j].v[0][ax]+T[j].v[1][ax]+T[j].v[2][ax];});int l=build(a,mid),r=build(mid,b);N[q].l=l;N[q].r=r;}return q;}
bool box(Node&n,V o,V d){D mn=0,mx=1e99L;for(int j=0;j<3;j++){if(fabsl(d[j])<1e-27L){if(o[j]<n.lo[j]-1e-9L||o[j]>n.hi[j]+1e-9L)return false;}else{D a=(n.lo[j]-1e-9L-o[j])/d[j],b=(n.hi[j]+1e-9L-o[j])/d[j];if(a>b)swap(a,b);mn=max(mn,a);mx=min(mx,b);if(mx<mn)return false;}}return true;}
D cr2(V a,V b,int u,int v){return a[u]*b[v]-a[v]*b[u];}
void scan(int k,V o,V d,Ray&r){auto&nd=N[k];if(!box(nd,o,d))return;if(nd.l>=0){scan(nd.l,o,d,r);scan(nd.r,o,d,r);return;}for(int j=nd.a;j<nd.b;j++){int fi=ids[j];auto&t=T[fi];V e1=t.v[1]-t.v[0],e2=t.v[2]-t.v[0],p=cross(d,e2),s=o-t.v[0];D det=dot(e1,p),dn=dot(d,t.n),plane=dot(s,t.n);if(fabsl(dn)<1e-12L&&fabsl(plane)<1e-10L){int ax=0;for(int x=1;x<3;x++)if(fabsl(t.n[x])>fabsl(t.n[ax]))ax=x;int x=(ax+1)%3,y=(ax+2)%3;D den=cr2(e1,e2,x,y),u=cr2(s,e2,x,y)/den,v=cr2(e1,s,x,y)/den,du=cr2(d,e2,x,y)/den,dv=cr2(e1,d,x,y)/den;D lo=0,hi=1e99L;D val[3]={u,v,1-u-v},slope[3]={du,dv,-du-dv};for(int z=0;z<3;z++){if(fabsl(slope[z])<1e-27L){if(val[z]<-1e-15L)lo=1e99L;}else if(slope[z]>0)lo=max(lo,-val[z]/slope[z]);else hi=min(hi,-val[z]/slope[z]);}if(hi-lo>1e-10L)r.b.push_back({lo,hi,plane,dn,fi});}
if(fabsl(det)<1e-27L)continue;D u=dot(s,p)/det;if(u< -1e-15L||u>1+1e-15L)continue;V q=cross(s,e1);D v=dot(d,q)/det;if(v< -1e-15L||u+v>1+1e-15L)continue;D z=dot(e2,q)/det;if(z>1e-12L)r.h.push_back({z,u,v,dn,fi});}}
Ray ray(V o,V d){Ray r;scan(0,o,d,r);sort(r.h.begin(),r.h.end(),[](Hit a,Hit b){return a.t<b.t;});return r;}
V readv(ifstream&f){double x[3];f.read((char*)x,24);return{{x[0],x[1],x[2]}};}
void print(ofstream&out,int i,Ray&r){out<<i;for(auto h:r.h)out<<';'<<h.t<<','<<h.f<<','<<h.u<<','<<h.v<<','<<h.nd;out<<'|';for(auto b:r.b)out<<';'<<b.a<<','<<b.b<<','<<b.f<<','<<b.plane<<','<<b.nd;out<<'\n';}
int main(int argc,char**argv){ifstream f(argv[1],ios::binary|ios::ate);int nf=f.tellg()/72;f.seekg(0);T.resize(nf);for(auto&t:T){for(auto&v:t.v)v=readv(f);t.n=norm(cross(t.v[1]-t.v[0],t.v[2]-t.v[0]));}for(int i=0;i<nf;i++)ids.push_back(i);build(0,nf);ifstream q(argv[2],ios::binary|ios::ate);int nr=q.tellg()/48;q.seekg(0);ofstream out(argv[3]);out<<setprecision(21);for(int i=0;i<nr;i++){V o=readv(q),d=readv(q);
if(argc>4){static ifstream ff(argv[4],ios::binary);int ix[2];ff.read((char*)ix,8);D weights[15][3]={{1.L/3,1.L/3,1.L/3},{.98L,.01L,.01L},{.01L,.98L,.01L},{.01L,.01L,.98L},{.495L,.495L,.01L},{.01L,.495L,.495L},{.495L,.01L,.495L},{.49L,.49L,.02L},{.49L,.02L,.49L},{.02L,.49L,.49L},{.8L,.1L,.1L},{.1L,.8L,.1L},{.1L,.1L,.8L},{.2L,.3L,.5L},{.2L,.5L,.3L}};auto&t=T[ix[0]];V p={{0,0,0}};for(int j=0;j<3;j++)p=p+t.v[j]*weights[ix[1]][j];o=p+t.n*1e-5L;d=t.n*(-1.L);}
auto r=ray(o,d);print(out,i,r);if(i%10000==0)cerr<<i<<'/'<<nr<<endl;}cerr<<nr<<" strict rays complete\n";}
