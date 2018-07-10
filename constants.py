def getBonusPointScaling(n_solved, difficulty):
    if  difficulty <= 10:
        return 0
    else:
        return {
            0: 0.3,
            1: 0.2,
            2: 0.1
        }.get(n_solved, 0)

def getBasePoints(difficulty):
    if difficulty <= 10:
        return 10
    elif difficulty <= 40:
        return 60
    elif difficulty <= 70:
        return 80
    else:
        return 100

def getRankConstant(n):
    return {
        1:'first',
        2:'second',
        3:'third'
    }.get(n, '')
