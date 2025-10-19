// Flattened C program to implement 2048 game

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h> // for Sleep

#define MAXRANDOMVALUE 3
#define MAXPREV 500

int main() {
    int arr[4][4] = {0}, c[4], temp = 0, len = 0, score = 0,
        highscore = 0, count = 0, ch = 0;
    int i, j, k, m, n, same = 0;
    char choise, s = -33, reschk;

    printf("===============2048==============\n");
    printf("WELCOME TO PUZZLE 2048\n");
    printf("> CONTROLS\n");
    printf("  FOR MOVES:- 'W','S','A','D'\n");
    printf("  GO BACKWARD:- 'P'\n");
    printf("  RESTART THE GAME:- 'R'\n");
    printf("  EXIT:-'U'\n");
    printf("\nPRESS ANY KEY TO START THE GAME....");
    getchar();

    system("clear || cls");
    printf("\n===============2048==============\n");
    printf("\nLOADING...\n");
    for (int i = 0, j; i < 35; i++) {
        printf("%c", s);
        j = i;
        if (i % 2 != 0 && i < 20) {
            Sleep(1);
        }
    }
    Sleep(1);
    system("clear || cls");

    // Allocate previous states
    int*** p;
    p = (int***)malloc(sizeof(int**) * (MAXPREV + 1));
    for (i = 0; i < MAXPREV + 1; i++) {
        p[i] = (int**)malloc(sizeof(int*) * 4);
        for (j = 0; j < 4; j++) {
            p[i][j] = (int*)malloc(sizeof(int) * 4);
        }
    }

    // Load highscore
    FILE* ptr = fopen("highscore.txt", "r");
    if(ptr) { fscanf(ptr, "%d", &highscore); fclose(ptr); }

    // Clear history
    ptr = fopen("hstr.txt", "w");
    fclose(ptr);

    // Add first random number
    srand(time(NULL));
    int ri, rj, no;
    do {
        ri = rand() % (MAXRANDOMVALUE + 1);
        rj = rand() % (MAXRANDOMVALUE + 1);
    } while (arr[ri][rj] != 0);
    no = 2 * ((rand() % 10) + 1);
    arr[ri][rj] = (no == 2 || no == 3) ? 4 : 2;

    while(1) {
        // Print the board
        system("clear || cls");
        printf("\n\t\t\t\t\t===============2048==============\n");
        printf("\t\t\t\t\tYOUR SCORE=%d\n\t\t\t\t\t", score);
        if (score < highscore) {
            printf("HIGH SCORE=%d\t\t\t\t\t\n", highscore);
        } else {
            highscore = score;
            printf("HIGH SCORE=%d\t\t\t\t\t\n", highscore);
        }
        printf("\t\t\t\t\t---------------------------------\n");
        for(i=0;i<4;i++){
            for(j=0;j<4;j++){
                if(j==0) printf("\t\t\t\t\t|");
                len=0;
                // Compute length of number
                int tmp=arr[i][j];
                if(tmp==0) len=0;
                else { while(tmp>0){ tmp/=10; len++; } }
                if(arr[i][j]!=0){
                    for(k=0;k<4-len;k++) printf(" ");
                    printf("%d", arr[i][j]);
                    for(k=0;k<4-len;k++) printf(" ");
                    for(k=0;k<len-1;k++) printf(" ");
                    printf("|");
                } else {
                    for(k=0;k<8-2*len-1;k++) printf(" ");
                    printf("|");
                }
            }
            if(i!=3) printf("\n\t\t\t\t\t-----------------------------"
                            "----\n");
        }
        printf("\n\t\t\t\t\t---------------------------------\n");
        printf("\t\t\t\t\tPREV-> P\t\t\t\t\t\n");
        printf("\t\t\t\t\tRESTART-> R\t\t\t\t\t\n");
        printf("\t\t\t\t\tEXIT-> U\t\t\t\t\t\n");
        printf("\t\t\t\t\tENTER YOUR CHOICE -> W,S,A,D\n\t\t\t\t\t");

        choise = getchar();
        while(getchar()!='\n');

        // Save previous state
        if (choise=='D'||choise=='d'||choise=='A'||choise=='a'||choise=='S'||choise=='s'||choise=='W'||choise=='w') {
            count++;
            ch++;
            if(count==MAXPREV+1){
                for(i=MAXPREV;i>0;i--)
                    for(j=0;j<4;j++)
                        for(k=0;k<4;k++)
                            p[i][j][k]=p[i-1][j][k];
                count=MAXPREV;
            }
            for(i=0;i<4;i++)
                for(j=0;j<4;j++)
                    p[MAXPREV-count][i][j]=arr[i][j];
        }

        // Move logic
        temp=0;
        if(choise=='D'||choise=='d'){
            for(i=0;i<4;i++){
                for(j=0;j<4;j++) c[j]=arr[i][j];
                // Update array right
                for(j=3;j>0;j--){
                    if(c[j]==c[j-1]){ c[j]+=c[j-1]; score+=c[j]; c[j-1]=0; temp=1; }
                    else if(c[j-1]==0 && c[j]!=0){ c[j-1]=c[j]; c[j]=0; temp=1; }
                    else if(c[j]==0) temp=1;
                }
                // Move values
                for(j=0;j<3;j++)
                    if(c[j]==0){ c[j]=c[j+1]; c[j+1]=0; }
                for(k=0;k<4;k++) arr[i][k]=c[k];
            }
        } else if(choise=='A'||choise=='a'){
            for(i=0;i<4;i++){
                for(j=0;j<4;j++) c[j]=arr[i][3-j];
                for(j=3;j>0;j--){
                    if(c[j]==c[j-1]){ c[j]+=c[j-1]; score+=c[j]; c[j-1]=0; temp=1; }
                    else if(c[j-1]==0 && c[j]!=0){ c[j-1]=c[j]; c[j]=0; temp=1; }
                    else if(c[j]==0) temp=1;
                }
                for(j=0;j<3;j++)
                    if(c[j]==0){ c[j]=c[j+1]; c[j+1]=0; }
                for(k=0;k<4;k++) arr[i][3-k]=c[k];
            }
        } else if(choise=='S'||choise=='s'){
            for(i=0;i<4;i++){
                for(j=0;j<4;j++) c[j]=arr[j][i];
                for(j=3;j>0;j--){
                    if(c[j]==c[j-1]){ c[j]+=c[j-1]; score+=c[j]; c[j-1]=0; temp=1; }
                    else if(c[j-1]==0 && c[j]!=0){ c[j-1]=c[j]; c[j]=0; temp=1; }
                    else if(c[j]==0) temp=1;
                }
                for(j=0;j<3;j++)
                    if(c[j]==0){ c[j]=c[j+1]; c[j+1]=0; }
                for(k=0;k<4;k++) arr[k][i]=c[k];
            }
        } else if(choise=='W'||choise=='w'){
            for(i=0;i<4;i++){
                for(j=0;j<4;j++) c[j]=arr[3-j][i];
                for(j=3;j>0;j--){
                    if(c[j]==c[j-1]){ c[j]+=c[j-1]; score+=c[j]; c[j-1]=0; temp=1; }
                    else if(c[j-1]==0 && c[j]!=0){ c[j-1]=c[j]; c[j]=0; temp=1; }
                    else if(c[j]==0) temp=1;
                }
                for(j=0;j<3;j++)
                    if(c[j]==0){ c[j]=c[j+1]; c[j+1]=0; }
                for(k=0;k<4;k++) arr[3-k][i]=c[k];
            }
        } else if(choise=='P'||choise=='p'){ // Previous
            if(count==0) { printf("\n******FURTHER MORE PREV NOT POSSIBLE********"); }
            else{
                ptr=fopen("hstr.txt","r+");
                int data;
                for(i=0;i<count;i++) fscanf(ptr,"%d",&data);
                fclose(ptr);
                score=data;
                for(i=0;i<4;i++)
                    for(j=0;j<4;j++)
                        arr[i][j]=p[MAXPREV-count][i][j];
                count--;
            }
        } else if(choise=='R'||choise=='r'){ // Reset
            score=0; count=0;
            for(i=0;i<4;i++)
                for(j=0;j<4;j++) arr[i][j]=0;
            // Add first random
            do { ri=rand()%(MAXRANDOMVALUE+1); rj=rand()%(MAXRANDOMVALUE+1); } while(arr[ri][rj]!=0);
            no = 2*((rand()%10)+1); arr[ri][rj]=(no==2||no==3)?4:2;
            continue;
        } else if(choise=='U'||choise=='u'){ exit(0); }

        // Add random number after valid move
        if(temp==1){
            do { ri=rand()%(MAXRANDOMVALUE+1); rj=rand()%(MAXRANDOMVALUE+1); } while(arr[ri][rj]!=0);
            no = 2*((rand()%10)+1); arr[ri][rj]=(no==2||no==3)?4:2;
        }

        // Check invalid key/game over
        same=0;
        for(m=0;m<4;m++){
            for(n=3;n>0;n--){
                if(arr[m][n]==arr[m][n-1] || arr[m][n]==0 || arr[m][n-1]==0) { same=1; break; }
                if(arr[n][m]==arr[n-1][m] || arr[m][n]==0 || arr[m][n-1]==0) { same=1; break; }
            }
            if(same==1) break;
        }
        if(same==1) { printf("\n============INVALID KEY==========\n"); continue; }
        else{
            printf("\n=============GAME OVER============");
            printf("\nWANT TO PLAY MORE?? Y/N??\n");
            reschk=getchar(); while(getchar()!='\n');
            if(reschk=='Y'||reschk=='y'){ score=0; count=0; for(i=0;i<4;i++) for(j=0;j<4;j++) arr[i][j]=0; continue; }
            else exit(0);
        }

        // Save highscore
        if(score>highscore){
            ptr=fopen("highscore.txt","w"); fprintf(ptr,"%d",score); fclose(ptr);
        }
    }

    return 0;
}
