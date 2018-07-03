#include<stdio.h>
#include<ctype.h>
#include<string.h>
#include<unistd.h>
void Tprime();
void Eprime();
void E(int a, int b);
void check(); 
void T();
 
 
char expression[10];
int count, flag;
 
int main()
{
      count = 0;
      flag = 0;
      printf("\nEnter an Algebraic Expression:\t");
      expression[0] = 'a';
      expression[1] = '*';
      expression[2] = 'b';      
      expression[3] = '\0';
      E(4, 7);
      if((strlen(expression) == count) && (flag == 0))
      {
            printf("\nThe Expression %s is Valid\n", expression);
      }
      else 
      {
            printf("\nThe Expression %s is Invalid\n", expression);
      }
      // sleep(1);
}
                    
void E(int a, int b)
{
      int c = a + b;
      T();
      Eprime();
}
 
void T()
{
      check();
      int  i;
      for(i = 0; i < 10; i++)
            printf("hello\n");
      Tprime();
}
 
void Tprime()
{
      if(expression[count] == '*')
      {
            count++;
            check();
            Tprime();
      }
}
 
void check()
{
      if(isalnum(expression[count]))
      {
            count++;
      }
      else if(expression[count] == '(')
      {
            count++;
            E(4, 7);
            if(expression[count] == ')')
            {
                  count++;
            }
            else
            {
                  flag = 1; 
            }
      }         
      else
      {
            flag = 1;
      }
}
 
void Eprime()
{
      if(expression[count] == '+')
      {
            count++;
            T();
            Eprime();
      }
}