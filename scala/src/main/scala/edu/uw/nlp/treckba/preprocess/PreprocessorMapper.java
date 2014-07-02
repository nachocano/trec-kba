package edu.uw.nlp.treckba.preprocess;


import edu.uw.nlp.treckba.gen.ContentItem;
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
            addTargetEntities("entities");
        } catch (IOException exc) {
            throw new RuntimeException("Exception while getting entities files. Exc " + exc.getMessage());
        }
    }


    private void addTargetEntities(String filename) throws IOException {
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

    private Text entity = new Text();

    public void map(Text key, StreamItemWritable value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
        if (value.isSetBody()) {
            ContentItem content = value.getBody();
            if (content.isSetClean_visible()) {
                String cleanVisible = content.getClean_visible().toLowerCase();
                for (String targetEntity : targetEntities) {
                    if (cleanVisible.indexOf(targetEntity) != -1) {
                        entity.set(targetEntity);
                        output.collect(entity, key);
                    }
                }
            }
        }
    }
}

