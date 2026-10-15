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
int main(int argc,char**argv){ifstream f(argv[1],ios::binary|ios::ate);int nf=f.tellg()/sizeof(Tri);f.seekg(0);T.resize(nf);f.read((char*)T.data(),nf*sizeof(Tri));for(int i=0;i<nf;i++)ids.push_back(i);build(0,nf);ofstream out(argv[2]);out<<setprecision(12)<<"face,sample,x,y,z,nx,ny,nz,entry,first_solid,air_after,exit_x,exit_y,exit_z,inside_control,outside_control,mid_control,after_exit_control,hits\n";double weights[7][3]={{1./3,1./3,1./3},{.98,.01,.01},{.01,.98,.01},{.01,.01,.98},{.495,.495,.01},{.01,.495,.495},{.495,.01,.495}};
for(int s=0;s<7;s++){for(int i=0;i<nf;i++){Tri&t=T[i];V n=cross(t.v[1]-t.v[0],t.v[2]-t.v[0]);n=n*(1/sqrt(dot(n,n)));V p=t.v[0]*weights[s][0]+t.v[1]*weights[s][1]+t.v[2]*weights[s][2],d=n*-1,o=p+n*1e-5;auto h=ray(o,d);double a=h.size()>0?h[0]:NAN,b=h.size()>1?h[1]:NAN,c=h.size()>2?h[2]:INFINITY;V e=o+d*b;double eps=min(1e-5,(c-b)/2);bool ic=inside(p-n*min(1e-5,(b-a)/4)),oc=inside(o),mc=inside(o+d*((a+b)/2)),ac=inside(e+d*eps);out<<i<<','<<s;for(double x:p.x)out<<','<<x;for(double x:n.x)out<<','<<x;out<<','<<a<<','<<b-a<<','<<c-b;for(double x:e.x)out<<','<<x;out<<','<<ic<<','<<oc<<','<<mc<<','<<ac<<',';for(double x:h)out<<x<<';';out<<'\n';}out.flush();cerr<<"SAMPLE "<<s<<" COMPLETE "<<(s+1)*nf<<endl;}}
