#include <bfd.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

long find_symbol(char *filename, char *symname)
{
    bfd *ibfd;
    asymbol **symtab;
    long nsize, nsyms, i;
    symbol_info syminfo;
    char **matching;

    bfd_init();
    ibfd = bfd_openr(filename, NULL);

    if (ibfd == NULL) {
        printf("bfd_openr error\n");
    }

    if (!bfd_check_format_matches(ibfd, bfd_object, &matching)) {
        printf("format_matches\n");
    }

    nsize = bfd_get_symtab_upper_bound (ibfd);
    symtab = malloc(nsize);
    nsyms = bfd_canonicalize_symtab(ibfd, symtab);

    for (i = 0; i < nsyms; i++) {
        if (strcmp(symtab[i]->name, symname) == 0) {
            bfd_symbol_info(symtab[i], &syminfo);
            return (long) syminfo.value;
        }
    }

    bfd_close(ibfd);
    printf("cannot find symbol\n");
}

int main()
{
    printf("%ld\n", find_symbol("a.out", "fact"));
    return 0;
}