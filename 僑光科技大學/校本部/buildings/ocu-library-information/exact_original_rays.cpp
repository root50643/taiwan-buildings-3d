#include <cmath>
#include <vector>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <algorithm>
using namespace std;using D=long double;struct V{D x,y,z;};V sub(V a,V b){return {a.x-b.x,a.y-b.y,a.z-b.z};}D dot(V a,V b){return a.x*b.x+a.y*b.y+a.z*b.z;}V cross(V a,V b){return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}struct T{V v,e1,e2,n;};struct H{D t,u,v,nd;int f;};
V readv(ifstream&f){double x[3];f.read((char*)x,24);return {x[0],x[1],x[2]};}
int main(int argc,char**argv){ifstream tf(argv[1],ios::binary|ios::ate);size_t nf=tf.tellg()/72;tf.seekg(0);vector<T>ts(nf);for(auto&t:ts){t.v=readv(tf);V b=readv(tf),c=readv(tf);t.e1=sub(b,t.v);t.e2=sub(c,t.v);t.n=cross(t.e1,t.e2);}ifstream qf(argv[2],ios::binary|ios::ate);size_t nq=qf.tellg()/48;qf.seekg(0);ofstream out(argv[3]);out<<setprecision(20);for(int i=0;i<nq;i++){V o=readv(qf),d=readv(qf);vector<H>h;for(int f=0;f<nf;f++){auto&t=ts[f];V p=cross(d,t.e2);D det=dot(t.e1,p);if(fabsl(det)<1e-27)continue;V s=sub(o,t.v);D u=dot(s,p)/det;if(u < -1e-15L||u>1+1e-15L)continue;V q=cross(s,t.e1);D v=dot(d,q)/det;if(v < -1e-15L||u+v>1+1e-15L)continue;D tt=dot(t.e2,q)/det;if(tt>1e-12L)h.push_back({tt,u,v,dot(t.n,d)/sqrtl(dot(t.n,t.n)),f});}sort(h.begin(),h.end(),[](H a,H b){return a.t<b.t;});out<<i;for(auto r:h)out<<';'<<r.t<<','<<r.f<<','<<r.u<<','<<r.v<<','<<r.nd;out<<'\n';if(i%500==0){out.flush();cerr<<i<<'/'<<nq<<endl;}}}
