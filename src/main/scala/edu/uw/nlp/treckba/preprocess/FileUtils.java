package edu.uw.nlp.treckba.preprocess;

import org.apache.commons.io.FilenameUtils;
import org.apache.hadoop.fs.*;
import org.apache.hadoop.mapred.JobConf;
import org.tukaani.xz.XZInputStream;

import java.io.IOException;
import java.util.Arrays;

/**
 * Decompression, decryption utils.
 * Decryption must be done in a local file in order to call gpg os process.
 * Decompression don't, but did it there anyway.
 * If performance is not good, we should copy back the decrypted file to hdfs
 * and continue from there.
 */
public class FileUtils {

    public static final String GPG_DIR = "GPG_DIR";
    public static final String TMP_DIR = "TMP_DIR";
    private static final String KEY_FILENAME = "trec-kba-rsa.txt";
    private static final String PATTERN = "/(.*\\.[xX][zZ]\\.[gG][pP][gG])$";

    private FileUtils() {
    }

    public static Path decrypt(Path path, JobConf conf) throws IOException {
        String dir = conf.get(FileUtils.GPG_DIR);
        if (!dir.endsWith("/")) {
            dir += "/";
        }
        String gpg = dir + "gpg";

        FileSystem fs = FileSystem.get(conf);
        LocalFileSystem lfs = LocalFileSystem.getLocal(conf);
        Path tmp = new Path(conf.get(FileUtils.TMP_DIR));
        //in distributed cache
        Path key = new Path(KEY_FILENAME);
        if (!lfs.exists(tmp)) {
            if (lfs.mkdirs(tmp)) {
                executeImport(gpg, tmp, key);
            } else {
                throw new IOException("Could not create local tmp folder");
            }
        }

        fs.copyToLocalFile(path, tmp);
        String gpgName = path.getName().split(PATTERN)[0];
        String xzName = FilenameUtils.removeExtension(gpgName);
        Path decryptedPath = new Path(tmp, xzName);
        executeDecryption(gpg, tmp, decryptedPath, new Path(tmp, gpgName));
        return decryptedPath;
    }

    private static void executeDecryption(String gpg, Path home, Path output, Path encrypted) throws IOException {
        String[] cmd = new String[]{gpg, "--no-permission-warning", "--homedir", home.toUri().toString(),
                "--trust-model", "always", "--output", output.toUri().toString(), "--decrypt", encrypted.toUri().toString()};
        System.out.println(Arrays.toString(cmd));
        run(cmd);
    }

    private static void executeImport(String gpg, Path home, Path key) throws IOException {
        String[] cmd = new String[]{gpg, "--no-permission-warning", "--homedir", home.toUri().toString(),
                "--import", key.toUri().toString()};
        System.out.println(Arrays.toString(cmd));
        run(cmd);
    }

    private static void run(String[] cmd) throws IOException {
        try {
            Runtime.getRuntime().exec(cmd).waitFor();
        } catch (InterruptedException exc) {
            System.err.println("Interrupted exc running " + Arrays.toString(cmd) + ". Exc " + exc.getMessage());
            throw new IOException(exc);
        } catch (IOException exc) {
            System.err.println("IOException running " + Arrays.toString(cmd) + ". Exc " + exc.getMessage());
            throw exc;
        }
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

  /*  public static final Path getFileFromCache(JobConf conf, String filename) throws IOException {
        Path[] files = DistributedCache.getLocalCacheFiles(conf);
        for (Path file : files) {
            if (file.getName().endsWith(filename)) {
                return file;
            }
        }
        return null;
    }
    */
}
