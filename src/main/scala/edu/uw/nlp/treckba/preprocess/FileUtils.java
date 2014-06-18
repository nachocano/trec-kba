package edu.uw.nlp.treckba.preprocess;

import org.apache.commons.compress.compressors.xz.XZCompressorInputStream;
import org.apache.commons.io.FilenameUtils;

import java.io.*;
import java.util.Arrays;

public class FileUtils {

    private FileUtils() {
    }

    public static String decrypt(String filename) throws IOException {
        String output = FilenameUtils.removeExtension(filename);
        System.out.println(output);
        String[] cmd = new String[]{"gpg", "-o", output, "-d", filename};
        try {
            Runtime.getRuntime().exec(cmd);
        } catch (IOException exc) {
            System.err.println("Error decrypting file " + Arrays.toString(cmd) + ". Exc " + exc.getMessage());
            throw exc;
        }
        return output;
    }

    public static String decompress(String filename) throws Exception {
        FileOutputStream out = null;
        XZCompressorInputStream xzIn = null;
        String output = FilenameUtils.removeExtension(filename);
        try {
            FileInputStream fin = new FileInputStream(filename);
            BufferedInputStream in = new BufferedInputStream(fin);
            xzIn = new XZCompressorInputStream(in);
            out = new FileOutputStream(output);
            final byte[] buffer = new byte[8 * 1024];
            int n = 0;
            while (-1 != (n = xzIn.read(buffer))) {
                out.write(buffer, 0, n);
            }
        } catch (Exception exc) {
            System.err.println("Error decompressing file " + filename + ". Exc " + exc.getMessage());
            throw exc;
        } finally {
            if (xzIn != null) {
                try {
                    xzIn.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if (out != null) {
                try {
                    out.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return output;
    }

    public static void decryptAndDecompress(String filename) throws Exception {
        String output = decrypt(filename);
        decompress(output);
    }

}
