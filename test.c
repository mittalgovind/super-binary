#include <stdio.h>
#include <string.h>

int fact(int n)
{
	return n<=1 ? 1 : n*fact(n-1);
}

void main()
{
	
	int ch=1, i, j;
	switch(ch)
	{
		case 1:
		printf("1\n");
		break;
		case 2:
		printf("%d\n", fact(ch));
		break;
	}

	for(i = 0; i < 2; i++)
	{
		printf("i\n");
		for(j = 0; j < 2; j++)
			printf("j\n");
	}
}