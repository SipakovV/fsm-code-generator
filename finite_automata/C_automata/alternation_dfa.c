
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

#define EOS '\0'


int parse(char* string) {

    int i = 0;
    bool accept;

s0:
    accept = true;
    printf("State: 0, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == '0') goto s1;
    if (string[i] == '1') goto s2;
    if (string[i] == EOS) goto end;
    goto error;

s1:
    accept = true;
    i++;
    printf("State: 1, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == '0') goto s3;
    if (string[i] == '1') goto s2;
    if (string[i] == EOS) goto end;
    goto error;

s2:
    accept = true;
    i++;
    printf("State: 2, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == '0') goto s1;
    if (string[i] == '1') goto s3;
    if (string[i] == EOS) goto end;
    goto error;

s3:
    accept = false;
    i++;
    printf("State: 3, accepts: %s, char: %c\n", accept ? "true" : "false", string[i]);
    if (string[i] == '0') goto s3;
    if (string[i] == '1') goto s3;
    if (string[i] == EOS) goto end;
    goto error;

error:
    printf("Error: Symbol not in alphabet!");
    exit(1);
    //return false;
    //throw

end:
    printf("End\n");
    return accept;
}


int main() {
    char input_string[40];
    printf("Enter string to parse (max 40 chars):\n");

    //scanf("%s", &input_string);
    gets(input_string);

    printf("%s\n", input_string);


    bool result = parse(input_string);
    printf("%s\n", result ? "true" : "false");


    return 0;
}
