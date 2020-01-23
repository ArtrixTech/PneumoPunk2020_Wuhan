function timeConvert(timesData) {
    //如果时间格式是正确的，那下面这一步转化时间格式就可以不用了
    var dateBegin = new Date(timesData);//将-转化为/，使用new Date
    var dateEnd = new Date();//获取当前时间
    var dateDiff = dateEnd.getTime() - dateBegin.getTime();//时间差的毫秒数
    var dayDiff = Math.floor(dateDiff / (24 * 3600 * 1000));//计算出相差天数
    var leave1 = dateDiff % (24 * 3600 * 1000)    //计算天数后剩余的毫秒数
    var hours = Math.floor(leave1 / (3600 * 1000))//计算出小时数
    //计算相差分钟数
    var leave2 = leave1 % (3600 * 1000)    //计算小时数后剩余的毫秒数
    var minutes = Math.floor(leave2 / (60 * 1000))//计算相差分钟数
    //计算相差秒数
    var leave3 = leave2 % (60 * 1000)      //计算分钟数后剩余的毫秒数
    var seconds = Math.round(leave3 / 1000);
    var timesString = '';

    if (dayDiff != 0) {
        timesString = dayDiff + '天前';
    } else if (dayDiff == 0 && hours != 0) {
        timesString = hours + '时前';
    } else if (dayDiff == 0 && hours == 0) {
        timesString = minutes + '分前';
    }

    return timesString
}
