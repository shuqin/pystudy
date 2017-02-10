def factorial(n):
	''' computing n*(n-1)*(n-2)*...*3*2*1 '''
	if n==0 or n==1 : 
		return 1;
	return n* factorial(n-1);

if __name__ == "__main__":
	print __name__;
	for i in range(10) : 
		print i,"! = " , factorial(i);
