#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "insanitythreadedtest.h"

#include <stdio.h>

/* if global vars are good enough for gstreamer, it's good enough for insanity */
static guint test_signal;

G_DEFINE_TYPE (InsanityThreadedTest, insanity_threaded_test,
    INSANITY_TEST_TYPE);

struct InsanityThreadedTestPrivateData
{
  GThread *thread;
};

static gpointer
test_thread_func (gpointer data)
{
  InsanityThreadedTest *test = INSANITY_THREADED_TEST (data);

  g_signal_emit (test, test_signal, 0, NULL);

  return NULL;
}

static gboolean
insanity_threaded_test_start (InsanityTest * itest)
{
  InsanityThreadedTest *test = INSANITY_THREADED_TEST (itest);

  printf ("insanity_threaded_test_start\n");

  if (!INSANITY_TEST_CLASS (insanity_threaded_test_parent_class)->start (itest))
    return FALSE;

  test->priv->thread =
#if GLIB_CHECK_VERSION(2,31,2)
  g_thread_new ("insanity_worker", test_thread_func, test);
#else
  g_thread_create (test_thread_func, test, TRUE, NULL);
#endif

  if (!test->priv->thread)
    return FALSE;

  return TRUE;
}

static void
insanity_threaded_test_test (InsanityThreadedTest * test)
{
  (void) test;
  printf ("insanity_test\n");
}

static void
insanity_threaded_test_init (InsanityThreadedTest * test)
{
  InsanityThreadedTestPrivateData *priv = G_TYPE_INSTANCE_GET_PRIVATE (test,
      INSANITY_THREADED_TEST_TYPE, InsanityThreadedTestPrivateData);

  test->priv = priv;
}

static void
insanity_threaded_test_class_init (InsanityThreadedTestClass * klass)
{
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);
  InsanityTestClass *test_class = INSANITY_TEST_CLASS (klass);

  test_class->start = &insanity_threaded_test_start;

  g_type_class_add_private (klass, sizeof (InsanityThreadedTestPrivateData));

  test_signal = g_signal_new ("test",
      G_TYPE_FROM_CLASS (gobject_class),
      G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
      G_STRUCT_OFFSET (InsanityThreadedTestClass, test),
      NULL, NULL, g_cclosure_marshal_VOID__VOID, G_TYPE_NONE /* return_type */ ,
      0, NULL);
}

InsanityThreadedTest *insanity_threaded_test_new(const char *name, const char *description)
{
  return g_object_new (insanity_threaded_test_get_type(), "name", name, "desc", description, NULL);
}

