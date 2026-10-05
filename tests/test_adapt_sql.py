import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("adapt_sql", Path(__file__).parents[1] / "cmake/adapt_sql.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SchemaProjection(unittest.TestCase):
    def test_quotes_and_idempotence(self):
        sql = "INSERT INTO item_template (entry,StatsCount,name) VALUES (1,2,'a,b; c''d'),(2,0,'x');"
        result = module.adapt(sql)
        self.assertNotIn("StatsCount", result)
        self.assertIn("(1, 'a,b; c''d')", result)
        self.assertEqual(result, module.adapt(result))

    def test_immunity_migration(self):
        result = module.adapt("INSERT INTO creature_template (entry,scale,mechanic_immune_mask,spell_school_immune_mask) VALUES (999,1,16,4);")
        self.assertIn("`CreatureImmunitiesId`", result)
        self.assertIn("(999, 999)", result)
        self.assertIn("(999, 4, 16,", result)

    def test_nonzero_trainer_and_multispawn_are_rejected(self):
        for sql in ["INSERT INTO creature_template (entry,trainer_type) VALUES (1,2);",
                    "INSERT INTO creature (guid,id1,id2,id3) VALUES (1,2,3,0);"]:
            with self.assertRaises(ValueError):
                module.adapt(sql)

    def test_insert_select_and_comments(self):
        result = module.adapt("-- note; ignored\nINSERT INTO item_template (entry,StatsCount,name) SELECT entry+1,2,CONCAT(name, ', suffix') FROM item_template WHERE entry=1 ON DUPLICATE KEY UPDATE name=VALUES(name);")
        self.assertNotIn("StatsCount", result)
        self.assertNotIn("DUPLICATE", result)
        self.assertIn("CONCAT(name, ', suffix')", result)

    def test_unquoted_legacy_spawn_columns(self):
        result = module.adapt("REPLACE INTO creature (guid,id1,id2,id3,map) VALUES (1,2,0,0,571);")
        self.assertIn("`guid`, `id`, `map`", result)
        self.assertIn("(1, 2, 571)", result)
        self.assertEqual(result, module.adapt(result))


if __name__ == "__main__":
    unittest.main()
