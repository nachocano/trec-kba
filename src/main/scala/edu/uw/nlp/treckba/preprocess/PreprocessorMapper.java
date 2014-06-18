package edu.uw.nlp.treckba.preprocess;


import edu.uw.nlp.treckba.gen.ContentItem;
import org.apache.commons.lang.Validate;
import org.apache.hadoop.filecache.DistributedCache;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.*;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;


public class PreprocessorMapper extends MapReduceBase implements Mapper<Text, StreamItemWritable, Text, Text> {


    private Set<String> targetEntities = new HashSet<String>();

    @Override
    public void configure(JobConf conf) {
        super.configure(conf);
        try {
            Path[] files = DistributedCache.getLocalCacheFiles(conf);
            //Validate.isTrue(files.length == 3);
            for (Path file : files) {
                String filename = file.toString();
                if (filename.contains("entities")) {
                    addTargetEntities(filename);
                } else if (filename.endsWith(".txt")){
                    //addDecryptionKey(filename);
                }
            }
        } catch (Exception exc) {
            System.err.println("Caught exception while getting cached files. Exc " + exc.getMessage());
        }

        try {
            Path[] files = DistributedCache.getLocalCacheFiles(conf);
            for (Path file : files) {
                if (file.toString().endsWith("gpg")) {
                    //FileUtils.decryptAndDecompress(file.toString());
                }
            }

        } catch (Exception exc) {
            System.err.println("Caught exception while trying to decrypt file. Exc " + exc.getMessage());
        }
    }

    private void addTargetEntities(String filename) throws Exception {
        BufferedReader bf = null;
        try {
            bf = new BufferedReader(new FileReader(filename));
            String line;
            while ((line = bf.readLine()) != null) {
                targetEntities.add(line.trim().toLowerCase());
            }
        } finally {
            if (bf != null) {
                bf.close();
            }
        }
        System.out.println("targetEntities " + Arrays.toString(targetEntities.toArray()));
    }

    private void addDecryptionKey(String filename) throws Exception {
        String[] cmd = new String[] {"gpg", "--import", filename};
        Runtime.getRuntime().exec(cmd);
    }

    private Text entity = new Text();

    public void map(Text key, StreamItemWritable value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
        ContentItem content = value.getBody();
        if (content != null) {
            String cleanVisible = content.getClean_visible();
            if (cleanVisible != null) {
                cleanVisible = cleanVisible.toLowerCase();
                for (String targetEntity: targetEntities) {
                    if (cleanVisible.indexOf(targetEntity) != -1) {
                        entity.set(targetEntity);
                        output.collect(entity, key);
                    }
                }
            }
        }
    }
}

