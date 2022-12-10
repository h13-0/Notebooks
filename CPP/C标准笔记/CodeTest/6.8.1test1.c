#include <stdio.h>

int main(int argc, char** argv)
{
    if(5 > 3)
    {
main :
        printf("jumped to label: \"main\"\r\n");
        goto end;
    }

    goto main;

end :
    return 0;
}
