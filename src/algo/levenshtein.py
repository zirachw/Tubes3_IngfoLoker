def lev(mat, i:int , j:int , a:int, b:int):
    mat[i][j] = min(mat[i-1][j] + 1, mat[i][j-1] + 1, mat[i-1][j-1] + (1 if a[j-1] != b[i-1] else  0))
    return mat
    

def levenshtein_distance(a:str, b: str) -> int:

    mat = [[0 for i in range(len(a)+1)] for j in range(len(b)+1)]

    for col in range(len(a)+1):
        mat[0][col] = col

    for row in range(len(b)+1):
        mat[row][0] = row


    for row in range(1,len(b)+1):
        for col in range(1,len(a)+1):
            mat = lev(mat,row,col,a,b)

    # for row in range(len(b)+1): # testing doang
    #     for col in range(len(a)+1):
    #         print(mat[row][col], end="")
    #     print("")

    return mat[len(b)][len(a)]

