namespace ChattingRoom.Core.Utils;
public static class NullCheck {
    public static bool NotNull(this object? obj) {
        return obj != null;
    }
    public static bool NotNull(this (object? a, object? b) o) {
        return o.a != null
            && o.b != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c) o) {
        return o.a != null
            && o.b != null
            && o.c != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f, object? g) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null
            && o.g != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f, object? g, object? h) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null
            && o.g != null
            && o.h != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f, object? g, object? h, object? i) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null
            && o.g != null
            && o.h != null
            && o.i != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f, object? g, object? h, object? i, object? j) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null
            && o.g != null
            && o.h != null
            && o.i != null
            && o.j != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f, object? g, object? h, object? i, object? j, object? k) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null
            && o.g != null
            && o.h != null
            && o.i != null
            && o.j != null
            && o.k != null;
    }
    public static bool NotNull(this (object? a, object? b, object? c, object? d, object? e, object? f, object? g, object? h, object? i, object? j, object? k, object? l) o) {
        return o.a != null
            && o.b != null
            && o.c != null
            && o.d != null
            && o.e != null
            && o.f != null
            && o.g != null
            && o.h != null
            && o.i != null
            && o.j != null
            && o.k != null
            && o.l != null;
    }
}