/* The following code was generated by JFlex 1.7.0-SNAPSHOT tweaked for IntelliJ platform */

package net.endlos.xdt99.xas99;

import com.intellij.lexer.FlexLexer;
import com.intellij.psi.tree.IElementType;
import net.endlos.xdt99.xas99.psi.Xas99Types;
import com.intellij.psi.TokenType;


/**
 * This class is a scanner generated by 
 * <a href="http://www.jflex.de/">JFlex</a> 1.7.0-SNAPSHOT
 * from the specification file <tt>Xas99.flex</tt>
 */
class Xas99Lexer implements FlexLexer {

  /** This character denotes the end of file */
  public static final int YYEOF = -1;

  /** initial size of the lookahead buffer */
  private static final int ZZ_BUFFERSIZE = 16384;

  /** lexical states */
  public static final int YYINITIAL = 0;
  public static final int MNEMONIC = 2;
  public static final int MNEMONICO = 4;
  public static final int ARGUMENTS = 6;
  public static final int COMMENT = 8;
  public static final int PREPROC = 10;

  /**
   * ZZ_LEXSTATE[l] is the state in the DFA for the lexical state l
   * ZZ_LEXSTATE[l+1] is the state in the DFA for the lexical state l
   *                  at the beginning of a line
   * l is of the form l = 2*k, k a non negative integer
   */
  private static final int ZZ_LEXSTATE[] = { 
     0,  0,  1,  1,  2,  2,  3,  3,  4,  4,  5, 5
  };

  /** 
   * Translates characters to character classes
   * Chosen bits are [7, 7, 7]
   * Total runtime size is 1672 bytes
   */
  public static int ZZ_CMAP(int ch) {
    return ZZ_CMAP_A[(ZZ_CMAP_Y[ZZ_CMAP_Z[ch>>14]|((ch>>7)&0x7f)]<<7)|(ch&0x7f)];
  }

  /* The ZZ_CMAP_Z table has 68 entries */
  static final char ZZ_CMAP_Z[] = zzUnpackCMap(
    "\1\0\103\200");

  /* The ZZ_CMAP_Y table has 256 entries */
  static final char ZZ_CMAP_Y[] = zzUnpackCMap(
    "\1\0\1\1\1\2\77\1\1\3\275\1");

  /* The ZZ_CMAP_A table has 512 entries */
  static final char ZZ_CMAP_A[] = zzUnpackCMap(
    "\11\0\1\62\1\63\2\0\1\41\22\0\1\61\1\43\1\51\1\56\1\57\1\54\1\60\1\50\1\70"+
    "\1\71\1\40\1\65\1\55\1\66\1\33\1\60\1\47\1\52\4\53\4\34\1\46\1\42\2\0\1\45"+
    "\1\0\1\64\1\1\1\2\1\3\1\24\1\12\1\30\1\14\1\16\1\36\1\11\1\37\1\17\1\4\1\21"+
    "\1\5\1\20\1\13\1\23\1\35\1\15\1\32\1\6\1\25\1\22\1\31\1\10\3\0\1\60\1\44\1"+
    "\0\1\1\1\2\1\3\1\24\1\12\1\30\1\14\1\16\1\36\1\11\1\37\1\17\1\4\1\21\1\5\1"+
    "\20\1\13\1\23\1\35\1\15\1\32\1\6\1\25\1\22\1\31\1\10\1\0\1\60\1\0\1\67\261"+
    "\0\2\26\115\0\1\7\52\0\1\27\125\0");

  /** 
   * Translates DFA states to action switch labels.
   */
  private static final int [] ZZ_ACTION = zzUnpackAction();

  private static final String ZZ_ACTION_PACKED_0 =
    "\6\0\1\1\1\2\1\3\1\4\1\5\1\2\1\6"+
    "\1\7\1\4\1\10\1\11\1\10\3\12\1\10\6\12"+
    "\1\11\2\12\1\1\1\12\1\1\1\10\2\12\1\13"+
    "\1\14\1\2\1\15\1\16\4\1\1\17\1\20\1\1"+
    "\1\21\1\22\1\23\1\24\1\25\1\26\1\27\1\30"+
    "\1\31\1\32\1\33\1\10\2\12\1\34\2\12\1\11"+
    "\2\12\1\10\11\12\1\0\1\10\6\0\4\12\2\35"+
    "\4\12\1\35\6\12\1\34\12\12\1\36\5\12\2\0"+
    "\1\12\1\37\1\12\1\10\10\12\2\40\2\15\1\0"+
    "\1\41\1\0\1\41\1\42\1\11\2\12\1\43\3\12"+
    "\1\44\4\12\1\10\1\45\1\0\1\35\1\10\4\0"+
    "\1\46\1\47\2\0\1\12\1\50\7\12\1\51\1\47"+
    "\1\12\1\36\1\52\1\44\2\12\1\53\3\12\1\11"+
    "\1\12\2\11\1\54\1\0\1\55\3\12\1\46\2\12"+
    "\1\54\1\12\1\56\1\57\1\60\1\61\1\56\1\10"+
    "\1\62\1\63\1\57\1\62\1\64\1\65\1\60\1\63";

  private static int [] zzUnpackAction() {
    int [] result = new int[219];
    int offset = 0;
    offset = zzUnpackAction(ZZ_ACTION_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackAction(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }


  /** 
   * Translates a state to a row index in the transition table
   */
  private static final int [] ZZ_ROWMAP = zzUnpackRowMap();

  private static final String ZZ_ROWMAP_PACKED_0 =
    "\0\0\0\72\0\164\0\256\0\350\0\u0122\0\u015c\0\u0196"+
    "\0\u01d0\0\u020a\0\u0244\0\u027e\0\u015c\0\u02b8\0\u015c\0\u02f2"+
    "\0\u032c\0\u0366\0\u03a0\0\u03da\0\u0414\0\u044e\0\u0488\0\u04c2"+
    "\0\u04fc\0\u0536\0\u0570\0\u05aa\0\u05e4\0\u061e\0\u0658\0\u0692"+
    "\0\u06cc\0\u0706\0\u0740\0\u077a\0\u07b4\0\u07ee\0\u0828\0\u0862"+
    "\0\u089c\0\u015c\0\u08d6\0\u0910\0\u094a\0\u0984\0\u015c\0\u015c"+
    "\0\u09be\0\u015c\0\u0828\0\u015c\0\u015c\0\u015c\0\u015c\0\u015c"+
    "\0\u015c\0\u09f8\0\u0a32\0\u015c\0\u0a6c\0\u0aa6\0\u0ae0\0\u0414"+
    "\0\u0b1a\0\u0b54\0\u0b8e\0\u0bc8\0\u0c02\0\u0414\0\u0c3c\0\u0c76"+
    "\0\u0cb0\0\u0cea\0\u0d24\0\u0d5e\0\u0d98\0\u0dd2\0\u0e0c\0\u0e46"+
    "\0\u0e80\0\u0eba\0\u0ef4\0\u0f2e\0\u0f68\0\u0fa2\0\u0fdc\0\u1016"+
    "\0\u1050\0\u108a\0\u10c4\0\u10fe\0\u1138\0\u1172\0\u11ac\0\u11e6"+
    "\0\u1220\0\u0414\0\u125a\0\u1294\0\u12ce\0\u1308\0\u1342\0\u137c"+
    "\0\u13b6\0\u13f0\0\u142a\0\u1464\0\u149e\0\u14d8\0\u1512\0\u154c"+
    "\0\u1586\0\u15c0\0\u15fa\0\u1634\0\u166e\0\u16a8\0\u16e2\0\u171c"+
    "\0\u1756\0\u1790\0\u17ca\0\u1804\0\u0706\0\u183e\0\u1878\0\u18b2"+
    "\0\u18ec\0\u1926\0\u1960\0\u199a\0\u19d4\0\u1a0e\0\u1a48\0\u0196"+
    "\0\u1a82\0\u08d6\0\u0910\0\u094a\0\u1abc\0\u0984\0\u015c\0\u09be"+
    "\0\u0414\0\u1af6\0\u1b30\0\u0414\0\u1b6a\0\u1ba4\0\u1bde\0\u0414"+
    "\0\u1c18\0\u1c52\0\u1c8c\0\u1cc6\0\u1d00\0\u1d3a\0\u1d74\0\u015c"+
    "\0\u1dae\0\u1de8\0\u1e22\0\u1e5c\0\u1e96\0\u015c\0\u015c\0\u1ed0"+
    "\0\u1f0a\0\u1f44\0\u0414\0\u1f7e\0\u1fb8\0\u1ff2\0\u202c\0\u2066"+
    "\0\u20a0\0\u20da\0\u0414\0\u0414\0\u2114\0\u0414\0\u0414\0\u214e"+
    "\0\u2188\0\u21c2\0\u0414\0\u21fc\0\u2236\0\u214e\0\u2270\0\u22aa"+
    "\0\u22e4\0\u015c\0\u015c\0\u231e\0\u0414\0\u2358\0\u2392\0\u23cc"+
    "\0\u0414\0\u2406\0\u2440\0\u0414\0\u247a\0\u0414\0\u0414\0\u0414"+
    "\0\u0414\0\u015c\0\u015c\0\u015c\0\u015c\0\u015c\0\u0414\0\u0414"+
    "\0\u0414\0\u015c\0\u0414";

  private static int [] zzUnpackRowMap() {
    int [] result = new int[219];
    int offset = 0;
    offset = zzUnpackRowMap(ZZ_ROWMAP_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackRowMap(String packed, int offset, int [] result) {
    int i = 0;  /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int high = packed.charAt(i++) << 16;
      result[j++] = high | packed.charAt(i++);
    }
    return j;
  }

  /** 
   * The transition table of the DFA
   */
  private static final int [] ZZ_TRANS = zzUnpackTrans();

  private static final String ZZ_TRANS_PACKED_0 =
    "\1\7\6\10\1\7\16\10\2\7\3\10\2\7\3\10"+
    "\1\11\1\12\1\13\1\14\1\10\1\7\1\15\12\7"+
    "\2\16\1\17\7\7\1\20\1\21\1\22\1\23\1\24"+
    "\1\25\1\26\1\25\1\27\1\30\2\25\1\31\1\25"+
    "\1\32\1\33\1\34\1\35\1\36\1\37\1\25\1\40"+
    "\1\7\2\25\1\41\1\42\1\7\1\43\1\44\1\25"+
    "\1\7\1\12\1\13\1\45\1\25\14\7\2\46\1\17"+
    "\47\7\1\12\1\13\16\7\2\47\1\17\7\7\6\10"+
    "\1\7\13\10\1\50\2\10\2\7\3\10\1\7\1\51"+
    "\3\10\1\52\1\12\1\13\1\14\1\10\1\53\1\54"+
    "\1\51\1\55\1\56\2\51\1\57\1\60\1\61\1\62"+
    "\1\57\1\63\1\47\1\17\1\64\1\65\1\66\1\67"+
    "\1\70\1\71\41\72\1\12\1\13\20\72\1\17\6\72"+
    "\41\73\1\12\1\13\12\73\1\74\3\73\1\63\1\47"+
    "\1\17\6\73\72\0\40\10\4\0\1\10\2\0\6\10"+
    "\1\0\1\10\13\0\41\11\1\0\21\11\1\0\6\11"+
    "\63\0\1\17\6\0\41\13\1\0\21\13\1\0\6\13"+
    "\40\10\3\0\1\14\1\10\2\0\6\10\1\0\1\10"+
    "\74\0\2\16\7\0\2\25\1\75\2\25\1\76\13\25"+
    "\1\77\4\25\1\100\7\25\1\100\1\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\3\25\1\101\3\25"+
    "\1\102\2\25\1\102\4\25\1\103\11\25\1\104\3\25"+
    "\1\102\2\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\1\25\1\105\1\106\2\25\1\107\1\25\1\110"+
    "\1\111\1\25\1\112\4\25\1\113\6\25\1\100\1\114"+
    "\5\25\1\110\1\100\1\114\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\5\25\1\115\12\25\1\116\17\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\23\25"+
    "\1\117\14\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\40\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\14\0\1\120\1\121\2\0\1\122\2\0\1\122\1\0"+
    "\1\123\2\0\1\124\1\0\1\125\3\0\1\126\1\0"+
    "\1\127\44\0\4\25\1\130\1\131\4\25\1\132\1\25"+
    "\1\133\1\25\1\134\1\135\1\25\1\136\16\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\6\25\1\137"+
    "\4\25\1\140\5\25\1\141\16\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\2\25\1\142\7\25\1\143"+
    "\13\25\1\144\7\25\1\144\1\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\5\25\1\145\15\25\1\146"+
    "\1\147\1\150\1\151\7\25\1\151\1\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\1\25\1\152\3\25"+
    "\1\153\1\25\1\110\2\25\1\112\13\25\1\154\3\25"+
    "\1\155\2\25\1\110\1\154\1\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\5\25\1\156\4\25\1\157"+
    "\25\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\5\25\1\160\32\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\5\25\1\161\1\25\1\162\2\25\1\163"+
    "\2\25\1\164\17\25\1\162\2\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\1\25\1\165\3\25\1\166"+
    "\1\25\1\110\2\25\1\167\7\25\1\170\3\25\1\171"+
    "\6\25\1\110\1\171\1\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\34\0\1\172\2\0\1\173\45\0\21\25"+
    "\1\174\16\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\14\0\6\175\1\0\16\175\2\0\3\175\1\0\4\175"+
    "\7\0\1\175\2\0\2\175\16\0\1\25\1\176\1\177"+
    "\2\25\1\200\2\25\1\200\1\25\1\201\2\25\1\202"+
    "\1\25\1\203\3\25\1\204\1\25\1\205\12\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\21\25\1\206"+
    "\2\25\1\207\13\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\40\25\3\0\1\45\1\25\2\0\6\25"+
    "\1\0\1\25\74\0\2\46\70\0\2\47\7\0\34\10"+
    "\1\210\3\10\4\0\1\10\2\0\1\210\2\10\1\211"+
    "\1\210\1\10\1\0\1\10\47\0\1\51\12\0\1\51"+
    "\2\0\2\51\17\0\3\212\6\0\1\212\11\0\1\212"+
    "\3\0\1\212\3\0\1\212\12\0\1\212\2\0\2\212"+
    "\65\0\1\213\2\0\1\213\17\0\41\214\1\0\6\214"+
    "\1\215\12\214\1\0\6\214\41\216\1\0\7\216\1\217"+
    "\11\216\1\0\6\216\34\0\1\220\12\0\1\220\2\0"+
    "\2\220\16\0\41\72\1\0\21\72\1\0\6\72\41\73"+
    "\1\0\13\73\1\0\3\73\3\0\6\73\7\25\1\221"+
    "\25\25\1\221\2\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\23\25\1\222\14\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\24\25\1\117\13\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\5\25\1\223"+
    "\32\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\7\25\1\224\25\25\1\224\2\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\25\25\1\225\12\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\15\25\1\226"+
    "\22\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\17\25\1\227\20\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\3\25\1\230\14\25\1\231\17\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\12\25\1\232"+
    "\25\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\3\25\1\230\34\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\21\25\1\233\16\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\23\25\1\221\14\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\5\25\1\234"+
    "\32\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\6\25\1\235\31\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\31\25\1\236\6\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\26\25\1\100\7\25\1\100"+
    "\1\25\4\0\1\25\2\0\6\25\1\0\1\25\21\0"+
    "\1\237\70\0\1\240\2\0\1\240\64\0\1\241\103\0"+
    "\1\242\57\0\1\243\3\0\1\244\15\0\1\245\7\0"+
    "\1\244\35\0\1\246\1\0\1\247\67\0\1\246\1\0"+
    "\1\246\6\0\1\250\4\0\1\246\72\0\1\251\51\0"+
    "\20\25\1\142\17\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\3\25\1\142\14\25\1\142\17\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\13\25\1\142"+
    "\24\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\15\25\1\142\22\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\12\25\1\142\25\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\12\25\1\142\2\25\1\142"+
    "\22\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\3\25\1\142\1\25\1\142\4\25\1\142\25\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\12\25\1\252"+
    "\25\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\32\25\1\224\5\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\24\25\1\253\13\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\22\25\1\254\15\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\15\25\1\255"+
    "\22\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\1\25\1\233\36\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\12\25\1\256\25\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\3\25\1\257\34\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\20\25\1\260"+
    "\17\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\4\25\1\260\2\25\1\261\25\25\1\261\2\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\14\25\1\262"+
    "\23\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\20\25\1\263\17\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\22\25\1\264\15\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\7\25\1\265\25\25\1\265"+
    "\2\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\20\25\1\266\17\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\14\25\1\221\23\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\20\25\1\267\2\25\1\270"+
    "\14\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\23\25\1\271\14\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\12\25\1\272\25\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\15\25\1\273\12\25\1\253"+
    "\7\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\25\25\1\274\12\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\15\25\1\275\22\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\23\25\1\276\14\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\3\25\1\277"+
    "\15\25\1\233\6\25\1\253\7\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\5\25\1\300\32\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\6\25\1\236"+
    "\31\25\4\0\1\25\2\0\6\25\1\0\1\25\16\0"+
    "\1\301\2\0\1\302\100\0\1\303\1\0\1\304\52\0"+
    "\17\25\1\305\20\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\6\25\1\226\31\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\5\25\1\142\2\25\1\142"+
    "\27\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\3\25\1\235\34\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\15\25\1\306\22\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\3\25\1\257\3\25\1\307"+
    "\15\25\1\310\7\25\1\307\2\25\4\0\1\25\2\0"+
    "\6\25\1\0\1\25\13\0\1\25\1\311\1\25\1\264"+
    "\34\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\1\25\1\311\1\25\1\311\6\25\1\312\4\25\1\311"+
    "\20\25\4\0\1\25\2\0\6\25\1\0\1\25\13\0"+
    "\20\25\1\313\17\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\3\25\1\277\2\25\1\221\31\25\4\0"+
    "\1\25\2\0\6\25\1\0\1\25\13\0\15\25\1\314"+
    "\1\25\1\315\20\25\4\0\1\25\2\0\6\25\1\0"+
    "\1\25\13\0\40\10\4\0\1\10\2\0\1\210\2\10"+
    "\2\210\1\10\1\0\1\10\63\0\1\214\21\0\14\25"+
    "\1\316\23\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\20\25\1\231\17\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\20\25\1\221\17\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\12\25\1\316\25\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\17\25"+
    "\1\263\20\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\31\25\1\314\6\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\14\25\1\317\23\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\24\25\1\317\13\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\21\25"+
    "\1\320\6\25\1\320\7\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\2\25\1\106\35\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\7\25\1\321\25\25"+
    "\1\321\2\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\25\0\1\322\61\0\1\323\74\0\1\302\107\0\1\324"+
    "\63\0\1\325\74\0\1\325\101\0\1\326\43\0\1\302"+
    "\67\0\21\25\1\305\16\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\15\25\1\314\22\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\17\25\1\314\20\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\22\25"+
    "\1\320\15\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\23\25\1\327\14\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\26\25\1\330\7\25\1\330\1\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\15\25"+
    "\1\305\22\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\12\25\1\305\25\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\16\25\1\263\21\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\14\25\1\224\23\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\14\25"+
    "\1\331\23\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\15\25\1\320\22\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\20\25\1\320\17\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\1\25\1\316\36\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\15\25"+
    "\1\221\22\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\20\25\1\305\17\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\30\0\1\302\66\0\1\332\57\0\5\25"+
    "\1\221\32\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\15\25\1\333\22\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0\20\25\1\333\17\25\4\0\1\25"+
    "\2\0\6\25\1\0\1\25\13\0\30\25\1\317\7\25"+
    "\4\0\1\25\2\0\6\25\1\0\1\25\13\0\2\25"+
    "\1\221\35\25\4\0\1\25\2\0\6\25\1\0\1\25"+
    "\13\0\12\25\1\320\25\25\4\0\1\25\2\0\6\25"+
    "\1\0\1\25\13\0";

  private static int [] zzUnpackTrans() {
    int [] result = new int[9396];
    int offset = 0;
    offset = zzUnpackTrans(ZZ_TRANS_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackTrans(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      value--;
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }


  /* error codes */
  private static final int ZZ_UNKNOWN_ERROR = 0;
  private static final int ZZ_NO_MATCH = 1;
  private static final int ZZ_PUSHBACK_2BIG = 2;

  /* error messages for the codes above */
  private static final String[] ZZ_ERROR_MSG = {
    "Unknown internal scanner error",
    "Error: could not match input",
    "Error: pushback value was too large"
  };

  /**
   * ZZ_ATTRIBUTE[aState] contains the attributes of state <code>aState</code>
   */
  private static final int [] ZZ_ATTRIBUTE = zzUnpackAttribute();

  private static final String ZZ_ATTRIBUTE_PACKED_0 =
    "\6\0\1\11\5\1\1\11\1\1\1\11\32\1\1\11"+
    "\4\1\2\11\1\1\1\11\1\1\6\11\2\1\1\11"+
    "\23\1\1\0\1\1\6\0\42\1\2\0\20\1\1\0"+
    "\1\1\1\0\1\11\17\1\1\0\1\11\1\1\4\0"+
    "\2\11\2\0\30\1\2\11\1\0\15\1\5\11\3\1"+
    "\1\11\1\1";

  private static int [] zzUnpackAttribute() {
    int [] result = new int[219];
    int offset = 0;
    offset = zzUnpackAttribute(ZZ_ATTRIBUTE_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackAttribute(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }

  /** the input device */
  private java.io.Reader zzReader;

  /** the current state of the DFA */
  private int zzState;

  /** the current lexical state */
  private int zzLexicalState = YYINITIAL;

  /** this buffer contains the current text to be matched and is
      the source of the yytext() string */
  private CharSequence zzBuffer = "";

  /** the textposition at the last accepting state */
  private int zzMarkedPos;

  /** the current text position in the buffer */
  private int zzCurrentPos;

  /** startRead marks the beginning of the yytext() string in the buffer */
  private int zzStartRead;

  /** endRead marks the last character in the buffer, that has been read
      from input */
  private int zzEndRead;

  /**
   * zzAtBOL == true <=> the scanner is currently at the beginning of a line
   */
  private boolean zzAtBOL = true;

  /** zzAtEOF == true <=> the scanner is at the EOF */
  private boolean zzAtEOF;

  /** denotes if the user-EOF-code has already been executed */
  private boolean zzEOFDone;


  /**
   * Creates a new scanner
   *
   * @param   in  the java.io.Reader to read input from.
   */
  Xas99Lexer(java.io.Reader in) {
    this.zzReader = in;
  }


  /** 
   * Unpacks the compressed character translation table.
   *
   * @param packed   the packed character translation table
   * @return         the unpacked character translation table
   */
  private static char [] zzUnpackCMap(String packed) {
    int size = 0;
    for (int i = 0, length = packed.length(); i < length; i += 2) {
      size += packed.charAt(i);
    }
    char[] map = new char[size];
    int i = 0;  /* index in packed string  */
    int j = 0;  /* index in unpacked array */
    while (i < packed.length()) {
      int  count = packed.charAt(i++);
      char value = packed.charAt(i++);
      do map[j++] = value; while (--count > 0);
    }
    return map;
  }

  public final int getTokenStart() {
    return zzStartRead;
  }

  public final int getTokenEnd() {
    return getTokenStart() + yylength();
  }

  public void reset(CharSequence buffer, int start, int end, int initialState) {
    zzBuffer = buffer;
    zzCurrentPos = zzMarkedPos = zzStartRead = start;
    zzAtEOF  = false;
    zzAtBOL = true;
    zzEndRead = end;
    yybegin(initialState);
  }

  /**
   * Refills the input buffer.
   *
   * @return      <code>false</code>, iff there was new input.
   *
   * @exception   java.io.IOException  if any I/O-Error occurs
   */
  private boolean zzRefill() throws java.io.IOException {
    return true;
  }


  /**
   * Returns the current lexical state.
   */
  public final int yystate() {
    return zzLexicalState;
  }


  /**
   * Enters a new lexical state
   *
   * @param newState the new lexical state
   */
  public final void yybegin(int newState) {
    zzLexicalState = newState;
  }


  /**
   * Returns the text matched by the current regular expression.
   */
  public final CharSequence yytext() {
    return zzBuffer.subSequence(zzStartRead, zzMarkedPos);
  }


  /**
   * Returns the character at position <tt>pos</tt> from the
   * matched text.
   *
   * It is equivalent to yytext().charAt(pos), but faster
   *
   * @param pos the position of the character to fetch.
   *            A value from 0 to yylength()-1.
   *
   * @return the character at position pos
   */
  public final char yycharat(int pos) {
    return zzBuffer.charAt(zzStartRead+pos);
  }


  /**
   * Returns the length of the matched text region.
   */
  public final int yylength() {
    return zzMarkedPos-zzStartRead;
  }


  /**
   * Reports an error that occured while scanning.
   *
   * In a wellformed scanner (no or only correct usage of
   * yypushback(int) and a match-all fallback rule) this method
   * will only be called with things that "Can't Possibly Happen".
   * If this method is called, something is seriously wrong
   * (e.g. a JFlex bug producing a faulty scanner etc.).
   *
   * Usual syntax/scanner level error handling should be done
   * in error fallback rules.
   *
   * @param   errorCode  the code of the errormessage to display
   */
  private void zzScanError(int errorCode) {
    String message;
    try {
      message = ZZ_ERROR_MSG[errorCode];
    }
    catch (ArrayIndexOutOfBoundsException e) {
      message = ZZ_ERROR_MSG[ZZ_UNKNOWN_ERROR];
    }

    throw new Error(message);
  }


  /**
   * Pushes the specified amount of characters back into the input stream.
   *
   * They will be read again by then next call of the scanning method
   *
   * @param number  the number of characters to be read again.
   *                This number must not be greater than yylength()!
   */
  public void yypushback(int number)  {
    if ( number > yylength() )
      zzScanError(ZZ_PUSHBACK_2BIG);

    zzMarkedPos -= number;
  }


  /**
   * Contains user EOF-code, which will be executed exactly once,
   * when the end of file is reached
   */
  private void zzDoEOF() {
    if (!zzEOFDone) {
      zzEOFDone = true;
    
    }
  }


  /**
   * Resumes scanning until the next regular expression is matched,
   * the end of input is encountered or an I/O-Error occurs.
   *
   * @return      the next token
   * @exception   java.io.IOException  if any I/O-Error occurs
   */
  public IElementType advance() throws java.io.IOException {
    int zzInput;
    int zzAction;

    // cached fields:
    int zzCurrentPosL;
    int zzMarkedPosL;
    int zzEndReadL = zzEndRead;
    CharSequence zzBufferL = zzBuffer;

    int [] zzTransL = ZZ_TRANS;
    int [] zzRowMapL = ZZ_ROWMAP;
    int [] zzAttrL = ZZ_ATTRIBUTE;

    while (true) {
      zzMarkedPosL = zzMarkedPos;

      zzAction = -1;

      zzCurrentPosL = zzCurrentPos = zzStartRead = zzMarkedPosL;

      zzState = ZZ_LEXSTATE[zzLexicalState];

      // set up zzAction for empty match case:
      int zzAttributes = zzAttrL[zzState];
      if ( (zzAttributes & 1) == 1 ) {
        zzAction = zzState;
      }


      zzForAction: {
        while (true) {

          if (zzCurrentPosL < zzEndReadL) {
            zzInput = Character.codePointAt(zzBufferL, zzCurrentPosL/*, zzEndReadL*/);
            zzCurrentPosL += Character.charCount(zzInput);
          }
          else if (zzAtEOF) {
            zzInput = YYEOF;
            break zzForAction;
          }
          else {
            // store back cached positions
            zzCurrentPos  = zzCurrentPosL;
            zzMarkedPos   = zzMarkedPosL;
            boolean eof = zzRefill();
            // get translated positions and possibly new buffer
            zzCurrentPosL  = zzCurrentPos;
            zzMarkedPosL   = zzMarkedPos;
            zzBufferL      = zzBuffer;
            zzEndReadL     = zzEndRead;
            if (eof) {
              zzInput = YYEOF;
              break zzForAction;
            }
            else {
              zzInput = Character.codePointAt(zzBufferL, zzCurrentPosL/*, zzEndReadL*/);
              zzCurrentPosL += Character.charCount(zzInput);
            }
          }
          int zzNext = zzTransL[ zzRowMapL[zzState] + ZZ_CMAP(zzInput) ];
          if (zzNext == -1) break zzForAction;
          zzState = zzNext;

          zzAttributes = zzAttrL[zzState];
          if ( (zzAttributes & 1) == 1 ) {
            zzAction = zzState;
            zzMarkedPosL = zzCurrentPosL;
            if ( (zzAttributes & 8) == 8 ) break zzForAction;
          }

        }
      }

      // store back cached position
      zzMarkedPos = zzMarkedPosL;

      if (zzInput == YYEOF && zzStartRead == zzCurrentPos) {
        zzAtEOF = true;
        zzDoEOF();
        return null;
      }
      else {
        switch (zzAction < 0 ? zzAction : ZZ_ACTION[zzAction]) {
          case 1: 
            { return TokenType.BAD_CHARACTER;
            }
          case 54: break;
          case 2: 
            { return Xas99Types.IDENT;
            }
          case 55: break;
          case 3: 
            { return Xas99Types.LCOMMENT;
            }
          case 56: break;
          case 4: 
            { yybegin(YYINITIAL); return Xas99Types.CRLF;
            }
          case 57: break;
          case 5: 
            { return Xas99Types.COMMENT;
            }
          case 58: break;
          case 6: 
            { return Xas99Types.OP_COLON;
            }
          case 59: break;
          case 7: 
            { yybegin(MNEMONIC); return TokenType.WHITE_SPACE;
            }
          case 60: break;
          case 8: 
            { return Xas99Types.INSTR_I;
            }
          case 61: break;
          case 9: 
            { return Xas99Types.INSTR_VI;
            }
          case 62: break;
          case 10: 
            { yybegin(COMMENT); return Xas99Types.UNKNOWN;
            }
          case 63: break;
          case 11: 
            { yybegin(ARGUMENTS); return TokenType.WHITE_SPACE;
            }
          case 64: break;
          case 12: 
            { yybegin(COMMENT); return TokenType.WHITE_SPACE;
            }
          case 65: break;
          case 13: 
            { return Xas99Types.INT;
            }
          case 66: break;
          case 14: 
            { return Xas99Types.OP_AST;
            }
          case 67: break;
          case 15: 
            { return Xas99Types.OP_MISC;
            }
          case 68: break;
          case 16: 
            { return Xas99Types.OP_SEP;
            }
          case 69: break;
          case 17: 
            { return Xas99Types.OP_LC;
            }
          case 70: break;
          case 18: 
            { return TokenType.WHITE_SPACE;
            }
          case 71: break;
          case 19: 
            { return Xas99Types.OP_AT;
            }
          case 72: break;
          case 20: 
            { return Xas99Types.OP_PLUS;
            }
          case 73: break;
          case 21: 
            { return Xas99Types.OP_MINUS;
            }
          case 74: break;
          case 22: 
            { return Xas99Types.OP_NOT;
            }
          case 75: break;
          case 23: 
            { return Xas99Types.OP_LPAREN;
            }
          case 76: break;
          case 24: 
            { return Xas99Types.OP_RPAREN;
            }
          case 77: break;
          case 25: 
            { yybegin(YYINITIAL); return Xas99Types.COMMENT;
            }
          case 78: break;
          case 26: 
            { return Xas99Types.PP_ARG;
            }
          case 79: break;
          case 27: 
            { return Xas99Types.PP_SEP;
            }
          case 80: break;
          case 28: 
            { return Xas99Types.INSTR_VIII;
            }
          case 81: break;
          case 29: 
            { return Xas99Types.INSTR_II;
            }
          case 82: break;
          case 30: 
            { yybegin(MNEMONICO); return Xas99Types.INSTR_O;
            }
          case 83: break;
          case 31: 
            { yybegin(PREPROC); return Xas99Types.PREP;
            }
          case 84: break;
          case 32: 
            { return Xas99Types.REGISTER;
            }
          case 85: break;
          case 33: 
            { return Xas99Types.TEXT;
            }
          case 86: break;
          case 34: 
            { return Xas99Types.PP_PARAM;
            }
          case 87: break;
          case 35: 
            { return Xas99Types.DIR_E;
            }
          case 88: break;
          case 36: 
            { return Xas99Types.INSTR_III;
            }
          case 89: break;
          case 37: 
            { return Xas99Types.INSTR_IX;
            }
          case 90: break;
          case 38: 
            { return Xas99Types.INSTR_V;
            }
          case 91: break;
          case 39: 
            { return Xas99Types.INSTR_F18A_II;
            }
          case 92: break;
          case 40: 
            { return Xas99Types.DIR_L;
            }
          case 93: break;
          case 41: 
            { return Xas99Types.INSTR_F18A_I;
            }
          case 94: break;
          case 42: 
            { return Xas99Types.INSTR_IX_X;
            }
          case 95: break;
          case 43: 
            { yybegin(MNEMONICO); return Xas99Types.INSTR_F18A_O;
            }
          case 96: break;
          case 44: 
            { return Xas99Types.DIR_S;
            }
          case 97: break;
          case 45: 
            { yybegin(MNEMONICO); return Xas99Types.DIR_O;
            }
          case 98: break;
          case 46: 
            { return Xas99Types.DIR_ES;
            }
          case 99: break;
          case 47: 
            { yybegin(MNEMONICO); return Xas99Types.DIR_X;
            }
          case 100: break;
          case 48: 
            { yybegin(MNEMONICO); return Xas99Types.INSTR_VII;
            }
          case 101: break;
          case 49: 
            { return Xas99Types.INSTR_9995;
            }
          case 102: break;
          case 50: 
            { return Xas99Types.INSTR_IV;
            }
          case 103: break;
          case 51: 
            { return Xas99Types.INSTR_VIII_R;
            }
          case 104: break;
          case 52: 
            { return Xas99Types.INSTR_VIII_I;
            }
          case 105: break;
          case 53: 
            { return Xas99Types.DIR_EO;
            }
          case 106: break;
          default:
            zzScanError(ZZ_NO_MATCH);
          }
      }
    }
  }


}