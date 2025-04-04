/*
**
We have a satellite observing the Earth's sky and monitoring the activity of the clouds. The satellite uses a Heat Radiation Index varying from 0 to 9 to determine if a particular spot in the sky is a cloud or not. Since clouds are colder, an index <= 4 can be considered a cloud.

The sky is represented as a two-dimensional array of integers containing the Heat Radiation Index.

We need to implement a method that returns the number of clouds that can be identified in the provided sky.

Note: a cloud is one or more connected cells with index <= 4. Cells are connected if they are horizontally or vertically adjacent to each other, not diagonally.

Examples:
*/

/*
 * 9 9 5 2
 * 8 8 1 5
 * 8 8 8 8
 * 9 9 9 4
*/
//This should return 3 (cells [0][3] and [1][2] are not connected).

/*
* 9 8 7 4 4 3 3 2 5 9
* 6 6 2 3 4 4 7 8 8 9
* 8 7 7 8 9 9 7 7 6 5
* 8 4 4 3 8 8 9 9 8 7
* 5 4 3 2 8 8 9 8 8 7
*/
//This should return 2.

/*
* 9 8 7 4 6 7 3 2 5 9
* 6 6 2 3 4 4 4 8 8 9
*/

/** 
 1 1 2 5 1


 */

class mapClouds {

  int maxRow, maxCol;

  int countClouds(int [][]mapdata, boolean[][]visited, int row, int col)
  {     

      if(row<0)
	return (0);
      if(col<0)
        return (0);

      if(row>=maxRow)
        return (0);
      if(col>=maxCol)
        return(0);

    //1 if we are in cloud and 0 if not
      if(! visited[row][col])
      {

        visited[row][col]=true;

        if(mapdata[row][col] <=4 ) ///at cloud    2
        {          
          countClouds(mapdata, visited, row, col+1);     //vist right
          countClouds(mapdata, visited, row+1, col);   //visit bottom
          countClouds(mapdata, visited, row, col-1);   //visit left      1
          countClouds(mapdata, visited, row-1, col);   //visit top      1

          countClouds(mapdata, visited, row-1, col-1);   //visit left      1
          countClouds(mapdata, visited, row+11, col+1);   //visit top      1

          return (1);
        }
        else
          return (0);
        
      }
      else
        return (0);


  }

  public boolean[] [] initVisited()
 {
   boolean[][] visited=new boolean[maxRow][maxCol];
   for(int r=0;r<maxRow;r++)
     for(int c=0;c<maxCol;c++)
      visited[r][c]=false;
  return (visited);
 }

  public int getCloudCount(int [][] mapdata)
  {
    boolean[][] visited=initVisited();     //all 0s equal tomxn

    int cloudCount=0;

    for(int r=0;r<maxRow;r++)
      for(int c=0;c<maxCol;c++)
        cloudCount += countClouds(mapdata, visited, r, c);


    return cloudCount;

  }

  public int [][] getData(int index)
  {
    int [][][] datas= 
{
{
 { 9, 9, 5, 2 },
 { 8, 8, 1, 5 },
 { 8, 8, 8, 8 },
 { 9, 9, 9, 4 }
},
{
{9,8,7,4,4,3,3,2,5,9},
{6,6,2,3,4,4,7,8,8,9},
{8,7,7,8,9,9,7,7,6,5},
{8,4,4,3,8,8,9,9,8,7},
{5,4,3,2,8,8,9,8,8,7}
},
{
{ 9, 8, 7, 4, 6, 7, 3, 2, 5, 9 },
{ 6, 6, 2, 3, 4, 4, 4, 8, 8, 9 },
},
{
{ 1, 1, 2, 5, 1 }
}

};

    int [][] data=datas[index];

    maxRow = data.length;
    maxCol = data[0].length;

    return data;
  }

  public static void main(String[] args){
    //Prints "Hello, World" to the terminal
	mapClouds mc=new mapClouds();

    for(int i=0;i<4;i++)
    {
      int [][]mapdata = mc.getData(i);
      int count = mc.getCloudCount(mapdata);
      System.out.println(count);
    }
  }

}
