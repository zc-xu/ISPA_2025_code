#将一个一维数组转化为二维数组，一维数组的内容是123456，需要变为 12 34 56
function arrayTo2D(arr,size){
    if(!arr.length) return [];
    const result = [];
    for (let i = 0 ; i < arr.length; i +=size){
        result.push(arr.slice(i,i + size));
    }
    return result;
}

const arr = [1,2,3,4,5,6];
console.log(arrayTo2D(arr,2));