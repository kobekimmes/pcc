import unittest
from unittest.mock import mock_open, patch
from src.c_lex import Lexer, ParseError


class LexerTest(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="abc 123\n")
    def test_init(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.eof, 8)
        self.assertEqual(lexer.source_code, "abc 123\n")
        self.assertEqual(lexer.file_pos, 0)
        self.assertEqual(lexer.line_no, 1)
        self.assertEqual(lexer.col_no, 1)
        
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init_fail(self, mock_file):
        pass
        

    @patch("builtins.open", new_callable=mock_open, read_data="abc123\n")
    def test_next_some(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.next(), "a")
        self.assertEqual(lexer.file_pos, 1)
        self.assertEqual(lexer.next(), "b")
        self.assertEqual(lexer.file_pos, 2)
        self.assertEqual(lexer.next(), "c")
        self.assertEqual(lexer.file_pos, 3)
        
        self.assertEqual(lexer.next(3), "123")
        self.assertEqual(lexer.file_pos, 6)
        
        self.assertEqual(lexer.next(), '\n')
        self.assertEqual(lexer.file_pos, 7)
        
        self.assertFalse(lexer.has_next())
        self.assertEqual(lexer.col_no, 1)
        self.assertEqual(lexer.line_no, 2)
        

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_next_none(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.next(), None)
        self.assertEqual(lexer.file_pos, 0)
        self.assertEqual(lexer.next(), None)
        self.assertEqual(lexer.file_pos, 0)
        self.assertEqual(lexer.next(), None)
        self.assertEqual(lexer.file_pos, 0)
        
        self.assertFalse(lexer.has_next())
        self.assertEqual(lexer.col_no, 1)
        self.assertEqual(lexer.line_no, 1)

    @patch("builtins.open", new_callable=mock_open, read_data="abc 123\n")
    def test_has_next_true(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertTrue(lexer.has_next())
        
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_has_next_false(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertFalse(lexer.has_next())

    @patch("builtins.open", new_callable=mock_open, read_data="abc 123\n")
    def test_peek_some(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.peek(), "a")
        self.assertEqual(lexer.peek(1), "a")
        self.assertEqual(lexer.peek(2), "ab")
        self.assertEqual(lexer.peek(3), "abc")
        self.assertEqual(lexer.file_pos, 0)
        
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_peek_none(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.peek(), None)
        self.assertEqual(lexer.peek(1), None)
        self.assertEqual(lexer.peek(2), None)
        self.assertEqual(lexer.peek(3), None)
        self.assertEqual(lexer.file_pos, 0)

    @patch("builtins.open", new_callable=mock_open, read_data="  .  random stuff going on here but stop at pause")
    def test_eat_until(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.eat_until("pause"), ".  random stuff going on here but stop at ")
        
    @patch("builtins.open", new_callable=mock_open, read_data="  .  random stuff going on here but stop at pause")
    def test_eat_while(self, mock_file):
        pass  # implement this test
    
    @patch("builtins.open", new_callable=mock_open, read_data="each one of these should be its own token but not this 0n3 . ")
    def test_token(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        self.assertEqual(lexer.token(), "each")
        self.assertEqual(lexer.file_pos, 5)
        self.assertEqual(lexer.token(), "one")
        self.assertEqual(lexer.file_pos, 9)
        self.assertEqual(lexer.token(), "of")
        self.assertEqual(lexer.file_pos, 12)
        self.assertEqual(lexer.token(), "these")
        self.assertEqual(lexer.file_pos, 18)
        self.assertEqual(lexer.token(), "should")
        self.assertEqual(lexer.file_pos, 25)
        self.assertEqual(lexer.token(), "be")
        self.assertEqual(lexer.file_pos, 28)
        self.assertEqual(lexer.token(), "its")
        self.assertEqual(lexer.file_pos, 32)
        self.assertEqual(lexer.token(), "own")
        self.assertEqual(lexer.file_pos, 36)
        self.assertEqual(lexer.token(), "token")
        self.assertEqual(lexer.file_pos, 42)
        self.assertEqual(lexer.token(), "but")
        self.assertEqual(lexer.token(), "not")
        self.assertEqual(lexer.token(), "this")
        with self.assertRaises(ParseError):
            lexer.token()
        
        self.assertNotEqual(lexer.token(), ".")
        self.assertEqual(lexer.file_pos, 59)
        
        
    @patch("builtins.open", new_callable=mock_open, read_data="10.0 0.0001 00054")
    def test_number(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        n1 = lexer.number()
        self.assertEqual(n1, "10.0")
        self.assertEqual(lexer.file_pos, 5)
        n2 = lexer.number()
        self.assertEqual(n2, "0.0001")
        self.assertEqual(lexer.file_pos, 12)
        
        with self.assertRaises(ParseError):
            n3 = lexer.number()
            
        
    @patch("builtins.open", new_callable=mock_open, read_data="\"hi this is a string\" this is not a string")
    def test_string(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        s1 = lexer.string()
        self.assertEqual(s1, "hi this is a string")
        self.assertEqual(lexer.file_pos, 20)
        s2 = lexer.string()
        self.assertEqual(s2, "")
        self.assertEqual(lexer.file_pos, 21)
        
        
        
    @patch("builtins.open", new_callable=mock_open, read_data="   \t     \n \t  \r  \n")
    def test_skip_whitespace(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        lexer.skip_whitespace()
        self.assertEqual(lexer.line_no, 3)
        self.assertEqual(lexer.col_no, 1)
        self.assertFalse(lexer.has_next())
        self.assertEqual(lexer.file_pos, lexer.eof)
        
        
    @patch("builtins.open", new_callable=mock_open, read_data="expect this and that")
    def test_expect_success(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        lexer.expect("expect ")
        self.assertEqual(lexer.file_pos, 7)
        lexer.expect("this ")
        self.assertEqual(lexer.file_pos, 12)
        lexer.expect("and ")
        self.assertEqual(lexer.file_pos, 16)
        lexer.expect("that")
        self.assertEqual(lexer.file_pos, 20)
        
        self.assertFalse(lexer.has_next())
        
        
    @patch("builtins.open", new_callable=mock_open, read_data="that was unexpected")
    def test_expect_failure(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        with self.assertRaises(ParseError):
            lexer.expect("this ")
        self.assertEqual(lexer.file_pos, 0)
    
    
    @patch("builtins.open", new_callable=mock_open, read_data="expect this or that")
    def test_expect_any_success(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        lexer.expect_any(["expect ", "anticipate "])
        self.assertEqual(lexer.file_pos, 7)
        lexer.expect_any(["that ", "this "])
        self.assertEqual(lexer.file_pos, 12)
        lexer.expect_any(["and ", "or "])
        self.assertEqual(lexer.file_pos, 15)
        lexer.expect_any(["this", "that"])
        self.assertEqual(lexer.file_pos, 19)
        
        self.assertFalse(lexer.has_next())
        
    @patch("builtins.open", new_callable=mock_open, read_data="didn't expect any of this")
    def test_expect_any_failure(self, mock_file):
        lexer = Lexer("fakefile.txt")
        self.assertEqual(lexer.file_pos, 0)
        with self.assertRaises(ParseError):
            lexer.expect_any(["shouldn't ", "don't ", "can't "])
        self.assertEqual(lexer.file_pos, 0)
        
        
        
class ParserTest(unittest.TestCase):
    
    def test_parse_expression():
        pass
    
    
    
    
if __name__ == "__main__":
    unittest.main()
