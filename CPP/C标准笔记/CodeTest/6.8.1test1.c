#include <stdint.h>

int main(int argc, char** argv)
{
    //

    if(5 > 10)
    {
    label_a :
        printf("Now we are jumped to label_a.");
        return 0;
    }
    
    main : 
    goto label_a;

    return -1;
}
