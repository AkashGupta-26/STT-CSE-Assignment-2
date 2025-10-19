#include <graphics.h>
#include <conio.h>
#include <stdio.h>
#include <stdlib.h>
#include <dos.h>

void main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "d:\\tc\\bgi");

    int arr[26][13];
    int i, j, k, score=0, spd=100, x, y, a, p, t_arr[6];
    char play='y', ch;

    // Initialize game board
    for(i=0;i<26;i++)
        for(j=0;j<13;j++)
            arr[i][j] = 0;
    for(i=0;i<26;i++) arr[i][0]=1;
    for(i=0;i<26;i++) arr[i][12]=1;
    for(j=0;j<13;j++) arr[25][j]=1;

    // Welcome screen and level selection
    while(play=='y') {
        cleardevice();
        settextstyle(2,0,6);
        outtextxy(200,100,"TETRIS GAME");
        outtextxy(100,200,"Select Level:");
        outtextxy(100,250,"1. Easy");
        outtextxy(100,300,"2. Medium");
        outtextxy(100,350,"3. Hard");

        ch = getch();
        if(ch=='1') spd=200;
        else if(ch=='2') spd=100;
        else if(ch=='3') spd=50;

        cleardevice();

        int shapeType, rotation, lx[4], ly[4];
        int nextShape, nextRot;

        // Generate first two shapes
        shapeType = rand()%7;
        rotation = 0;
        nextShape = rand()%7;
        nextRot = 0;

        while(1) {
            // Starting coordinates
            x=5; y=0;
            switch(shapeType) {
                case 0: // I
                    if(rotation%2==0){ lx[0]=x; lx[1]=x; lx[2]=x; lx[3]=x; ly[0]=y; ly[1]=y+1; ly[2]=y+2; ly[3]=y+3; }
                    else { lx[0]=x-1; lx[1]=x; lx[2]=x+1; lx[3]=x+2; ly[0]=y; ly[1]=y; ly[2]=y; ly[3]=y; }
                    break;
                case 1: // O
                    lx[0]=x; lx[1]=x+1; lx[2]=x; lx[3]=x+1;
                    ly[0]=y; ly[1]=y; ly[2]=y+1; ly[3]=y+1;
                    break;
                case 2: // T
                    if(rotation%4==0){ lx[0]=x-1; lx[1]=x; lx[2]=x+1; lx[3]=x; ly[0]=y; ly[1]=y; ly[2]=y; ly[3]=y+1; }
                    else if(rotation%4==1){ lx[0]=x; lx[1]=x; lx[2]=x; lx[3]=x+1; ly[0]=y-1; ly[1]=y; ly[2]=y+1; ly[3]=y; }
                    else if(rotation%4==2){ lx[0]=x-1; lx[1]=x; lx[2]=x+1; lx[3]=x; ly[0]=y; ly[1]=y; ly[2]=y; ly[3]=y-1; }
                    else { lx[0]=x; lx[1]=x; lx[2]=x; lx[3]=x-1; ly[0]=y-1; ly[1]=y; ly[2]=y+1; ly[3]=y; }
                    break;
                case 3: // S
                    if(rotation%2==0){ lx[0]=x; lx[1]=x+1; lx[2]=x-1; lx[3]=x; ly[0]=y; ly[1]=y; ly[2]=y+1; ly[3]=y+1; }
                    else { lx[0]=x; lx[1]=x; lx[2]=x+1; lx[3]=x+1; ly[0]=y; ly[1]=y+1; ly[2]=y-1; ly[3]=y; }
                    break;
                case 4: // Z
                    if(rotation%2==0){ lx[0]=x-1; lx[1]=x; lx[2]=x; lx[3]=x+1; ly[0]=y; ly[1]=y; ly[2]=y+1; ly[3]=y+1; }
                    else { lx[0]=x+1; lx[1]=x+1; lx[2]=x; lx[3]=x; ly[0]=y; ly[1]=y+1; ly[2]=y-1; ly[3]=y; }
                    break;
                case 5: // J
                    if(rotation%4==0){ lx[0]=x-1; lx[1]=x-1; lx[2]=x; lx[3]=x+1; ly[0]=y; ly[1]=y+1; ly[2]=y; ly[3]=y; }
                    else if(rotation%4==1){ lx[0]=x; lx[1]=x; lx[2]=x; lx[3]=x+1; ly[0]=y-1; ly[1]=y; ly[2]=y+1; ly[3]=y+1; }
                    else if(rotation%4==2){ lx[0]=x-1; lx[1]=x; lx[2]=x+1; lx[3]=x+1; ly[0]=y; ly[1]=y; ly[2]=y; ly[3]=y-1; }
                    else { lx[0]=x-1; lx[1]=x; lx[2]=x; lx[3]=x; ly[0]=y-1; ly[1]=y-1; ly[2]=y; ly[3]=y+1; }
                    break;
                case 6: // L
                    if(rotation%4==0){ lx[0]=x-1; lx[1]=x; lx[2]=x+1; lx[3]=x+1; ly[0]=y; ly[1]=y; ly[2]=y; ly[3]=y+1; }
                    else if(rotation%4==1){ lx[0]=x; lx[1]=x; lx[2]=x; lx[3]=x+1; ly[0]=y-1; ly[1]=y; ly[2]=y+1; ly[3]=y-1; }
                    else if(rotation%4==2){ lx[0]=x-1; lx[1]=x-1; lx[2]=x; lx[3]=x+1; ly[0]=y-1; ly[1]=y; ly[2]=y; ly[3]=y; }
                    else { lx[0]=x; lx[1]=x; lx[2]=x; lx[3]=x-1; ly[0]=y-1; ly[1]=y; ly[2]=y+1; ly[3]=y+1; }
                    break;
            }

            // Drop block
            int landed=0;
            while(!landed) {
                // Draw block
                for(i=0;i<4;i++){
                    setcolor(WHITE);
                    setfillstyle(SOLID_FILL,6);
                    rectangle(180+lx[i]*15,90+ly[i]*15,180+lx[i]*15+14,90+ly[i]*15+14);
                    floodfill(181+lx[i]*15,91+ly[i]*15,WHITE);
                }

                delay(spd);

                // Clear block
                for(i=0;i<4;i++){
                    setcolor(BLACK);
                    setfillstyle(SOLID_FILL,BLACK);
                    rectangle(180+lx[i]*15,90+ly[i]*15,180+lx[i]*15+14,90+ly[i]*15+14);
                    floodfill(181+lx[i]*15,91+ly[i]*15,BLACK);
                }

                // Check collision below
                for(i=0;i<4;i++){
                    if(arr[ly[i]+1][lx[i]]==1) { landed=1; break; }
                }

                if(!landed) for(i=0;i<4;i++) ly[i]++;

                // Keyboard input
                if(kbhit()){
                    char c = getch();
                    if(c==0) c=getch();
                    if(c==75){ // Left
                        int canMove=1;
                        for(i=0;i<4;i++) if(arr[ly[i]][lx[i]-1]==1) canMove=0;
                        if(canMove) for(i=0;i<4;i--) lx[i]--;
                    }
                    if(c==77){ // Right
                        int canMove=1;
                        for(i=0;i<4;i++) if(arr[ly[i]][lx[i]+1]==1) canMove=0;
                        if(canMove) for(i=0;i<4;i++) lx[i]++;
                    }
                    if(c==32){ // Rotate
                        rotation = (rotation+1)%4;
                        break; // Recalculate shape positions next loop
                    }
                    if(c==27) exit(0); // ESC exit
                }
            }

            // Place block in array
            for(i=0;i<4;i++) arr[ly[i]][lx[i]]=1;

            // Check complete lines
            for(i=24;i>=0;i--){
                int full=1;
                for(j=1;j<12;j++){
                    if(arr[i][j]==0){ full=0; break; }
                }
                if(full){
                    score+=100;
                    for(k=i;k>0;k--) for(j=1;j<12;j++) arr[k][j]=arr[k-1][j];
                    for(j=1;j<12;j++) arr[0][j]=0;
                    i++; // recheck same line
                }
            }

            // Check Game Over
            for(i=1;i<12;i++){
                if(arr[0][i]==1){
                    settextstyle(3,0,4);
                    outtextxy(200,200,"GAME OVER");
                    outtextxy(200,250,"Press Y to play again");
                    char tmp=getch();
                    if(tmp!='y') exit(0);
                    // reset board
                    for(i=0;i<26;i++) for(j=0;j<13;j++) arr[i][j]=0;
                    for(i=0;i<26;i++) arr[i][0]=1;
                    for(i=0;i<26;i++) arr[i][12]=1;
                    for(j=0;j<13;j++) arr[25][j]=1;
                    score=0;
                    break;
                }
            }

            shapeType = nextShape;
            rotation = nextRot;
            nextShape = rand()%7;
            nextRot = 0;
        }
    }

    closegraph();
}