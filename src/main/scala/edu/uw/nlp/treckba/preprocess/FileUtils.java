package edu.uw.nlp.treckba.preprocess;

import org.apache.commons.io.FilenameUtils;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.tukaani.xz.XZInputStream;

import java.io.IOException;
import java.util.Arrays;

public class FileUtils {

    public static final String GPG_DIR = "GPG_DIR";

    private FileUtils() {
    }

    public static Path decrypt(String dir, Path path, FileSystem fs)  throws IOException {
        Path decryptedPath = removeExtension(path);
        if (!dir.endsWith("/")) {
            dir += "/";
        }
        String[] cmd = new String[]{dir + "gpg", "--decrypt", path.toUri().toString()};
        System.out.println(Arrays.toString(cmd));
        try {
            Runtime.getRuntime().exec(cmd).waitFor();
        } catch (InterruptedException exc) {
            System.err.println("Interrupted exc decrypting file " + Arrays.toString(cmd) + ". Exc " + exc.getMessage());
        } catch (IOException exc) {
            System.err.println("Error decrypting file " + Arrays.toString(cmd) + ". Exc " + exc.getMessage());
            throw exc;
        }
        return decryptedPath;
    }

    public static Path decompress(Path path, FileSystem fs) throws IOException {
        XZInputStream xzIn = null;
        FSDataOutputStream out = null;
        FSDataInputStream in = null;
        Path uncompressedPath = removeExtension(path);
        try {
            in = fs.open(path);
            xzIn = new XZInputStream(in);
            out = fs.create(uncompressedPath);
            final byte[] buffer = new byte[8 * 1024];
            int n;
            while ((n = xzIn.read(buffer)) != -1) {
                out.write(buffer, 0, n);
            }
        } catch (IOException exc) {
            System.err.println("Exception unxz-ing file " + path.toUri().toString() + ". Exc " + exc.getMessage());
            throw exc;
        } finally {
            if (xzIn != null) {
                xzIn.close();
            }
            if (in != null) {
                in.close();
            }
            if (out != null) {
                out.close();
            }
        }
        return uncompressedPath;
    }

    private static Path removeExtension(Path path) {
        String newFilename = FilenameUtils.removeExtension(path.toUri().toString());
        return new Path(newFilename);
    }

}
