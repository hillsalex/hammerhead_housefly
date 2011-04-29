inputFile = 'adj.dat';
outputFile = 'pageRank.dat';


% Get number of lines
fid = fopen(inputFile,'rt');
N = 0;
while (fgets(fid) ~= -1),
  N = N+1;
end
fclose(fid);

display(N)

fid = fopen(inputFile);

M = sparse(N,N);

tline = fgets(fid);
docID = 0;
linenum = 0;
while ischar(tline)
    A = sscanf(tline, '%d');
    M(docID+1,A+1) = 1;
    docID = docID + 1;
    tline = fgets(fid);
    if mod(linenum,1000)==0
       display(linenum) 
    end
    linenum = linenum + 1;
end

display('Done creating adjacency matrix')

G = transpose(M);
n = N;

display('A')
alpha = 0.1;
p = 1-alpha;
c = sum(G,1);

display('B')

k = find(c~=0);
D = sparse(k,k,1./c(k),n,n);
e = ones(n,1);

display('C')

I = speye(n,n);

G = p*G*D;

display('E')

z = ((1-p)*(c~=0) + (c==0))/n;
x = e/n;

for i=1:128
   x = G*x + e*(z*x); 
end

display(x)
display(size(x,2))

% Output results
dlmwrite(outputFile, x, 'delimiter', '\n', 'precision', '%.12f')
fclose(resFile);
fclose(fid);
display('done')