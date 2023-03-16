#include <stdio.h>
#include <stdbool.h>

int main() {

    char ch;
    bool accept;

s:
    printf("State: S\n");
    accept = false;
    scanf("%c", &ch);
    printf("%c\n", ch);
    if (ch == 'm') goto m;
    if (ch == EOF) goto end;
    goto s;
m:
    printf("State: M\n");
    accept = false;
    scanf("%c", &ch);
    printf("%c\n", ch);
    if (ch == 'm') goto m;
    if (ch == 'a') goto a;
    if (ch == EOF) goto end;
    goto s;
a:
    printf("State: A\n");
    accept = false;
    scanf("%c", &ch);
    printf("%c\n", ch);
    if (ch == 'm') goto m;
    if (ch == 'i') goto i;
    if (ch == EOF) goto end;
    goto s;
i:
    printf("State: I\n");
    accept = false;
    scanf("%c", &ch);
    printf("%c\n", ch);
    if (ch == 'm') goto m;
    if (ch == 'n') goto n;
    if (ch == EOF) goto end;
    goto s;
n:
    printf("State: N, accept\n");
    accept = true;
    while (scanf("%c", &ch));
end:
    printf("State: End\n");
    if (accept) {
        printf("+\n");
    }
    else {
        //printf("%c", c);
        printf("-\n");
    }



    return 0;
}
