
#include <stdio.h>
#include <stdbool.h>

#define EOS '\0'


int parse(char* string) {

    int i = 0;
    bool accept;

s:
    accept = false;
    printf("State: S, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == 'm') goto m;
    if (string[i] == EOS) goto end;
    goto trash;

m:
    accept = false;
    i++;
    printf("State: M, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == 'a') goto a;
    if (string[i] == EOS) goto end;
    goto trash;

a:
    accept = false;
    i++;
    printf("State: A, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == 'i') goto i;
    if (string[i] == EOS) goto end;
    goto trash;

i:
    accept = false;
    i++;
    printf("State: I, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == 'n') goto n;
    if (string[i] == EOS) goto end;
    goto trash;

n:
    accept = true;
    i++;
    printf("State: N, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == EOS) goto end;
    goto trash;

trash:
    accept = false;
    i++;
    printf("State: Trash, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == EOS) goto end;
    goto trash;

end:
    printf("End\n");
    return accept;
}


int main() {
/*
    char string[] = "abcdefghi";
    char* s;

    for (s=&string[0]; *s != '\0'; s++ )
    {
        printf("%c\n", *s);
    }
    */
    char input_string[40];
    printf("Enter string to parse (max 40 chars):\n");

    //scanf("%s", &input_string);
    gets(input_string);

    printf("%s\n", input_string);


    bool result = parse(input_string);
    printf("%s\n", result ? "true" : "false");


    return 0;
}
