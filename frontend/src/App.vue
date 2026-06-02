<template>
    <RouterView />
</template>

<style>
:root {
    color: #1d2433;
    background: #f5f7fb;
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
}

button {
    font: inherit;
}

h1,
h2,
p {
    margin-top: 0;
}

.page-shell {
    max-width: 1180px;
    margin: 0 auto;
    padding: 32px;
}

@media (max-width: 760px) {
    .page-shell {
        padding: 18px;
    }
}
</style>
