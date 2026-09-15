#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>

#define MAX 64

// Note: lowercase letters are all remapped via a fixed substitution cipher.
char flag[MAX] = "L3AK{ngx_qkt_fgz_ugffq_uxtll_dt}";
char input[MAX];

// A full lowercase substitution: a->q, b->w, c->e, d->r, e->t, f->y, g->u,
// h->i, i->o, j->p, k->a, l->s, m->d, n->f, o->g, p->h, q->j, r->k,
// s->l, t->z, u->x, v->c, w->v, x->b, y->n, z->m
char remap[128];

void init_remap() {
    for (int i = 0; i < 128; i++) remap[i] = i;
    // apply full lowercase mapping
    remap['a'] = 'q'; remap['b'] = 'w'; remap['c'] = 'e'; remap['d'] = 'r';
    remap['e'] = 't'; remap['f'] = 'y'; remap['g'] = 'u'; remap['h'] = 'i';
    remap['i'] = 'o'; remap['j'] = 'p'; remap['k'] = 'a'; remap['l'] = 's';
    remap['m'] = 'd'; remap['n'] = 'f'; remap['o'] = 'g'; remap['p'] = 'h';
    remap['q'] = 'j'; remap['r'] = 'k'; remap['s'] = 'l'; remap['t'] = 'z';
    remap['u'] = 'x'; remap['v'] = 'c'; remap['w'] = 'v'; remap['x'] = 'b';
    remap['y'] = 'n'; remap['z'] = 'm';
}

void sigint_handler(int sig) {
    // On Ctrl-C, reshuffle two lowercase mappings at random
    char a = 'a' + (rand() % 26);
    char b = 'a' + (rand() % 26);
    char t = remap[a]; remap[a] = remap[b]; remap[b] = t;
    write(1, "[interrupt remap]\n", 17);
}

int main() {
    srand(time(NULL));
    init_remap();
    signal(SIGINT, sigint_handler);

    printf("Enter flag: ");
    fflush(stdout);
    fgets(input, MAX, stdin);
    for (int i = 0; input[i]; i++) {
        unsigned char c = input[i];
        if (c < 128)
            input[i] = remap[c];
    }

    if (!strncmp(input, flag, strlen(flag))) {
        puts("YEEY!");
    } else {
        puts("YEET!");
    }
    return 0;
}
