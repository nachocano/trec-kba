package edu.uw.nlp.treckba.preprocess;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

import java.io.IOException;
import java.util.Iterator;

public class PreprocessorReducer extends MapReduceBase implements Reducer<Text, Text, Text, Text> {

    public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
        System.out.println("key in reducer " + key.toString());
        StringBuilder sb = new StringBuilder();
        while (values.hasNext()) {
            sb.append(values.next().toString()).append(",");
        }
        sb.deleteCharAt(sb.length()-1);
        System.out.println("sb in reducer " + sb.toString());
        output.collect(key, key);
    }
}

