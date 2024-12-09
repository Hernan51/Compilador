main {
    int N, a, b, temp, i;

    cin N;

    a = 0;
    b = 1;

    if (N == 1) {
        cout a;
    } else {
        if (N == 2) {
        cout b;
        }
    } else {
        for (i = 3; i <= N; i++) {
            temp = a + b;
            a = b;
            b = temp;
        }
        cout b;
    }
}
