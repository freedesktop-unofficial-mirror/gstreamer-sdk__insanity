#ifndef INSANITY_H_GUARD
#define INSANITY_H_GUARD

#include <glib.h>
#include <glib-object.h>

struct InsanityTestPrivateData;
typedef struct InsanityTestPrivateData InsanityTestPrivateData;

struct InsanityTest;
typedef struct InsanityTest InsanityTest;

struct InsanityTest {
  GObject parent;

  InsanityTestPrivateData *priv;
};

struct InsanityTestClass
{
  GObjectClass parent_class;

  gboolean (*setup) (InsanityTest *test);
  gboolean (*start) (InsanityTest *test);
  void (*stop) (InsanityTest *test);
};
typedef struct InsanityTestClass InsanityTestClass;


/* Handy macros */
#define INSANITY_TEST_TYPE                (insanity_test_get_type ())
#define INSANITY_TEST(obj)                (G_TYPE_CHECK_INSTANCE_CAST ((obj), INSANITY_TEST_TYPE, InsanityTest))
#define INSANITY_TEST_CLASS(c)            (G_TYPE_CHECK_CLASS_CAST ((c), INSANITY_TEST_TYPE, InsanityTestClass))
#define IS_INSANITY_TEST(obj)             (G_TYPE_CHECK_TYPE ((obj), INSANITY_TEST_TYPE))
#define IS_INSANITY_TEST_CLASS(c)         (G_TYPE_CHECK_CLASS_TYPE ((c), INSANITY_TEST_TYPE))
#define INSANITY_TEST_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS ((obj), INSANITY_TEST_TYPE, InsanityTestClass))

GType insanity_test_get_type (void);

gboolean insanity_test_get_argument(InsanityTest *test, const char *key, GValue *value);
char *insanity_test_get_output_filename(InsanityTest *test, const char *key);
void insanity_test_done(InsanityTest *test);
void insanity_test_validate_step(InsanityTest *test, const char *name, gboolean success);
void insanity_test_add_extra_info(InsanityTest *test, const char *name, const GValue *data);

gboolean insanity_test_run(InsanityTest *test, int argc, const char **argv);

#endif

