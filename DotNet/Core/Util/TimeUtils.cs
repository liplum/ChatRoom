namespace ChattingRoom.Core.Utils;
public static class TimeUtils {
    public static DateTime ToUnixDatetime(this long unixSeconds) {
        var offset = DateTimeOffset.FromUnixTimeSeconds(unixSeconds);
        return offset.DateTime;
    }
}