#include <cmath>
#include <vector>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <algorithm>
using namespace std;
using D=long double;
struct V{D x,y,z;};V sub(V a,V b){return {a.x-b.x,a.y-b.y,a.z-b.z};}D dot(V a,V b){return a.x*b.x+a.y*b.y+a.z*b.z;}V cross(V a,V b){return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
struct T{V v[3];};
int main(int argc,char**argv){ifstream tf(argv[1],ios::binary|ios::ate);size_t nf=tf.tellg()/72;tf.seekg(0);vector<T>ts(nf);for(auto&t:ts)for(auto&v:t.v){double x[3];tf.read((char*)x,24);v={x[0],x[1],x[2]};}ifstream pf(argv[2],ios::binary|ios::ate);size_t np=pf.tellg()/24;pf.seekg(0);vector<V>ps(np);for(auto&p:ps){double x[3];pf.read((char*)x,24);p={x[0],x[1],x[2]};}ofstream out(argv[3]);out<<setprecision(20);for(int i=0;i<np;i++){D sum=0,err=0;V p=ps[i];for(auto&t:ts){V a=sub(t.v[0],p),b=sub(t.v[1],p),c=sub(t.v[2],p);D la=sqrtl(dot(a,a)),lb=sqrtl(dot(b,b)),lc=sqrtl(dot(c,c));D n=dot(a,cross(b,c));D den=la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb;D x=atan2l(n,den)-err;D total=sum+x;err=(total-sum)-x;sum=total;}out<<i<<','<<sum/(2*acosl(-1))<<'\n';if(i%500==0){out.flush();cerr<<i<<'/'<<np<<endl;}}}
