def quicksort(a,l,r):
    if(l<r):
        temp = a[l];i = l;j = r
        while(i<j):
            while(i<j and a[j]>=temp):
                j=j-1
            if(i<j):
                a[i]=a[j]
                i = i+1
            while(i<j and a[i]<=temp):
                i=i+1
            if(i<j):
                a[j]=a[i]
                j = j-1
        a[i]=temp
        quicksort(a,l,i-1)
        quicksort(a,i+1,r)
if __name__ == '__main__':
    a = [4,2,55,2,7,2,7,2,4,1,8]
    print a
    quicksort(a,0,len(a)-1)
    print a