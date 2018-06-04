#include <stdio.h>

int bar (int j)
{
	printf("%d\n", j);
	return 0;
}

int foo(int *p, int b)
{
	int a;
	if(b)
		bar(123);
	else
		bar(321);
	a = *p;
	if(p == 0)
		return 0;

	return 0;
}

int main()
{
	int i = 10;
	foo(&i, i);
	return 0;
}