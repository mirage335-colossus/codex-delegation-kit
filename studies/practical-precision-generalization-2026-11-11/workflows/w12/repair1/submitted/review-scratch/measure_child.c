#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
int main(int argc, char **argv) {
  if (argc < 2) return 2;
  pid_t child = fork();
  if (child < 0) return 125;
  if (child == 0) { execvp(argv[1], argv + 1); perror("execvp"); _exit(127); }
  int status = 0; struct rusage usage;
  while (wait4(child, &status, 0, &usage) < 0) if (errno != EINTR) return 125;
  fprintf(stderr, "CHILD_RSS_KIB %ld\n", usage.ru_maxrss);
  if (WIFEXITED(status)) return WEXITSTATUS(status);
  if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
  return 125;
}