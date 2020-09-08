

import org.apache.commons.codec.binary.Base64;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class GitHubAccessTokenScrambler12 {
    static final String myInitVector = "RandomInitVector";
    static final  String myKey = "GitHubErrorToken";

    static String encrypt(String value) {
         try { 
             IvParameterSpec iv = new IvParameterSpec(myInitVector.getBytes("UTF-8"));
             SecretKeySpec keySpec = new SecretKeySpec(myKey.getBytes("UTF-8"), "AES");

             Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5PADDING");
             cipher.init(Cipher.ENCRYPT_MODE, keySpec, iv);

             byte[] encrypted = cipher.doFinal(value.getBytes());
             return Base64.encodeBase64String(encrypted);
         } catch (Exception ex) {
             ex.printStackTrace();
         }
         return null;
     }
}
