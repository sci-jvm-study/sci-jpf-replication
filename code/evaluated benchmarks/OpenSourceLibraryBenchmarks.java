package research;

public class OpenSourceLibraryBenchmarks {

    private static int sink(int val) {
        return val > 0 ? 1 : -1;
    }

    // 1. Google Guava
    public static int guavaPreconditionsReal(int index, int size) {
        int state = 0;
        try {
            if (index < 0 || index >= size) {
                throw new IndexOutOfBoundsException("index out of bounds");
            }
            state = index + 1;
        } catch (IndexOutOfBoundsException e) {
            state = -1;
        }
        return sink(state);
    }

    public static int guavaPreconditionsControl(int index, int size) {
        int state = 0;
        if (index < 0 || index >= size) {
            state = -1;
        } else {
            state = index + 1;
        }
        return sink(state);
    }

    // 2. Apache Commons Lang
    static class CharHolder {
        int c;
        CharHolder(int c) { this.c = c; }
        boolean isDigit() { return c >= 48 && c <= 57; } // '0' is 48, '9' is 57
    }

    public static int commonsLangReal(int char1, int char2) {
        CharHolder h1 = new CharHolder(char1);
        CharHolder h2 = new CharHolder(char2);
        int state = 0;
        if (h1.isDigit() && h2.isDigit()) {
            state = 100;
        } else {
            state = 10;
        }
        return sink(state);
    }

    public static int commonsLangControl(int char1, int char2) {
        int state = 0;
        if (char1 >= 48 && char1 <= 57 && char2 >= 48 && char2 <= 57) {
            state = 100;
        } else {
            state = 10;
        }
        return sink(state);
    }

    // 3. Apache Commons Math
    static class Fraction {
        int num, den;
        Fraction(int n, int d) { num = n; den = d; }
        Fraction add(Fraction other) {
            return new Fraction(this.num * other.den + other.num * this.den, this.den * other.den);
        }
    }

    public static int commonsMathReal(int num1, int den1, int num2, int den2) {
        if (den1 == 0 || den2 == 0) return -1;
        Fraction f1 = new Fraction(num1, den1);
        Fraction f2 = new Fraction(num2, den2);
        Fraction res = f1.add(f2);
        return sink(res.num);
    }

    public static int commonsMathControl(int num1, int den1, int num2, int den2) {
        if (den1 == 0 || den2 == 0) return -1;
        int resNum = num1 * den2 + num2 * den1;
        return sink(resNum);
    }

    // 4. Google Gson
    static class Escaper {
        boolean needsEscape(int c) {
            return c == 34 || c == 92; // '\"' is 34, '\\' is 92
        }
    }

    public static int gsonJsonWriterReal(int c1, int c2) {
        Escaper esc = new Escaper();
        int state = 0;
        if (esc.needsEscape(c1) || esc.needsEscape(c2)) {
            state = 50;
        } else {
            state = 5;
        }
        return sink(state);
    }

    public static int gsonJsonWriterControl(int c1, int c2) {
        int state = 0;
        if (c1 == 34 || c1 == 92 || c2 == 34 || c2 == 92) {
            state = 50;
        } else {
            state = 5;
        }
        return sink(state);
    }

    // 5. Jackson Core
    interface Decoder { int decode(int b); }
    static class AsciiDecoder implements Decoder { public int decode(int b) { return b; } }
    static class MultiByteDecoder implements Decoder { public int decode(int b) { return b - 128; } }
    static final Decoder asciiDec = new AsciiDecoder();
    static final Decoder mbDec = new MultiByteDecoder();

    public static int jacksonUtf8Real(int b1, int b2) {
        int r1, r2;
        if (b1 < 128) {
            r1 = asciiDec.decode(b1);
        } else {
            r1 = mbDec.decode(b1);
        }
        if (b2 < 128) {
            r2 = asciiDec.decode(b2);
        } else {
            r2 = mbDec.decode(b2);
        }
        int res = r1 + r2;
        return sink(res);
    }

    public static int jacksonUtf8Control(int b1, int b2) {
        int r1 = (b1 < 128) ? b1 : (b1 - 128);
        int r2 = (b2 < 128) ? b2 : (b2 - 128);
        int res = r1 + r2;
        return sink(res);
    }

    // 6. Joda-Time
    static class YearVal {
        int year;
        YearVal(int y) { year = y; }
        void validate() throws IllegalArgumentException {
            if (year < 0 || year > 9999) {
                throw new IllegalArgumentException("Invalid year");
            }
        }
    }

    public static int jodaLocalDateReal(int year) {
        int state = 0;
        try {
            new YearVal(year).validate();
            state = 1;
        } catch (IllegalArgumentException e) {
            state = 0;
        }
        return sink(state);
    }

    public static int jodaLocalDateControl(int year) {
        int state = 0;
        if (year < 0 || year > 9999) {
            state = 0;
        } else {
            state = 1;
        }
        return sink(state);
    }

    // 7. Apache Commons Collections
    static class Node {
        int val;
        Node next;
        Node(int v) { val = v; }
    }

    public static int commonsCollectionsReal(int op1, int op2) {
        Node head = new Node(op1);
        Node tail = new Node(op2);
        head.next = tail;
        int state = 0;
        if (head.val > tail.val) {
            state = 200;
        } else {
            state = 20;
        }
        return sink(state);
    }

    public static int commonsCollectionsControl(int op1, int op2) {
        int state = 0;
        if (op1 > op2) {
            state = 200;
        } else {
            state = 20;
        }
        return sink(state);
    }

    // 8. Apache Commons IO
    static class PathScanner {
        int c1, c2;
        PathScanner(int a, int b) { c1 = a; c2 = b; }
        boolean hasSeparator() { return c1 == 47 || c1 == 92 || c2 == 47 || c2 == 92; } // '/' is 47, '\\' is 92
    }

    public static int commonsIoReal(int pathChar1, int pathChar2) {
        PathScanner scanner = new PathScanner(pathChar1, pathChar2);
        int state = 0;
        if (scanner.hasSeparator()) {
            state = 300;
        } else {
            state = 30;
        }
        return sink(state);
    }

    public static int commonsIoControl(int pathChar1, int pathChar2) {
        int state = 0;
        if (pathChar1 == 47 || pathChar1 == 92 || pathChar2 == 47 || pathChar2 == 92) {
            state = 300;
        } else {
            state = 30;
        }
        return sink(state);
    }

    // 9. Apache Commons Codec
    static class Base64Lookup {
        boolean isValid(int b) {
            return (b >= 65 && b <= 90) || (b >= 97 && b <= 122) || (b >= 48 && b <= 57) || b == 43 || b == 47;
        }
    }

    public static int commonsCodecReal(int b1, int b2) {
        Base64Lookup lookup = new Base64Lookup();
        int state = 0;
        if (lookup.isValid(b1) && lookup.isValid(b2)) {
            state = 400;
        } else {
            state = 40;
        }
        return sink(state);
    }

    public static int commonsCodecControl(int b1, int b2) {
        boolean v1 = (b1 >= 65 && b1 <= 90) || (b1 >= 97 && b1 <= 122) || (b1 >= 48 && b1 <= 57) || b1 == 43 || b1 == 47;
        boolean v2 = (b2 >= 65 && b2 <= 90) || (b2 >= 97 && b2 <= 122) || (b2 >= 48 && b2 <= 57) || b2 == 43 || b2 == 47;
        int state = 0;
        if (v1 && v2) {
            state = 400;
        } else {
            state = 40;
        }
        return sink(state);
    }

    // 10. SLF4J
    static class FormattedMessage {
        int c1, c2;
        FormattedMessage(int a, int b) { c1 = a; c2 = b; }
        boolean isLoggable() { return c1 > 50 && c2 > 50; }
    }

    public static int slf4jReal(int code1, int code2) {
        FormattedMessage msg = new FormattedMessage(code1, code2);
        int state = 0;
        if (msg.isLoggable()) {
            state = 500;
        } else {
            state = 50;
        }
        return sink(state);
    }

    public static int slf4jControl(int code1, int code2) {
        int state = 0;
        if (code1 > 50 && code2 > 50) {
            state = 500;
        } else {
            state = 50;
        }
        return sink(state);
    }

    public static int guavaPreconditionsScaled6(
        int s1, int s2, int s3, int s4, int s5, int s6, int size) {
        int total = 0;
        total += guavaPreconditionsReal(s1, size);
        total += guavaPreconditionsReal(s2, size);
        total += guavaPreconditionsReal(s3, size);
        total += guavaPreconditionsReal(s4, size);
        total += guavaPreconditionsReal(s5, size);
        total += guavaPreconditionsReal(s6, size);
        return sink(total);
    }

    public static int guavaPreconditionsScaled9(
        int s1, int s2, int s3, int s4, int s5, int s6, int s7, int s8, int s9, int size) {
        int total = 0;
        total += guavaPreconditionsReal(s1, size);
        total += guavaPreconditionsReal(s2, size);
        total += guavaPreconditionsReal(s3, size);
        total += guavaPreconditionsReal(s4, size);
        total += guavaPreconditionsReal(s5, size);
        total += guavaPreconditionsReal(s6, size);
        total += guavaPreconditionsReal(s7, size);
        total += guavaPreconditionsReal(s8, size);
        total += guavaPreconditionsReal(s9, size);
        return sink(total);
    }

    // Main Method calling each with concrete values
    public static void main(String[] args) {
        guavaPreconditionsReal(0, 3);
        guavaPreconditionsControl(0, 3);
        commonsLangReal(48, 48);
        commonsLangControl(48, 48);
        commonsMathReal(1, 2, 1, 3);
        commonsMathControl(1, 2, 1, 3);
        gsonJsonWriterReal(97, 98);
        gsonJsonWriterControl(97, 98);
        jacksonUtf8Real(120, 120);
        jacksonUtf8Control(120, 120);
        jodaLocalDateReal(2000);
        jodaLocalDateControl(2000);
        commonsCollectionsReal(1, 2);
        commonsCollectionsControl(1, 2);
        commonsIoReal(47, 47);
        commonsIoControl(47, 47);
        commonsCodecReal(65, 65);
        commonsCodecControl(65, 65);
        slf4jReal(60, 60);
        slf4jControl(60, 60);
        guavaPreconditionsScaled6(0, 0, 0, 0, 0, 0, 3);
        guavaPreconditionsScaled9(0, 0, 0, 0, 0, 0, 0, 0, 0, 3);
    }
}
