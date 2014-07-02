package edu.uw.nlp.treckba.preprocess;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;


public class PreprocessorDriver extends Configured implements Tool {


    @Override
    public int run(String[] args) throws Exception {
        JobConf conf = new JobConf(getConf(), PreprocessorDriver.class);
        conf.setJobName("treckba-preprocess");

        conf.setJarByClass(PreprocessorDriver.class);
        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Text.class);

        conf.setMapperClass(PreprocessorMapper.class);
        conf.setReducerClass(PreprocessorReducer.class);
        conf.setCombinerClass(PreprocessorReducer.class);

        conf.setInputFormat(ThriftFileInputFormat.class);
        conf.setOutputFormat(TextOutputFormat.class);

        FileInputFormat.setInputPaths(conf, new Path(args[0]));
        FileSystem.get(conf).delete(new Path(args[1]), true);
        FileOutputFormat.setOutputPath(conf, new Path(args[1]));

        FileSystem.getLocal(conf).delete(new Path(conf.get(FileUtils.TMP_DIR)), true);

        JobClient.runJob(conf);
        return 0;
    }


    public static void main(String args[]) throws Exception {
        Configuration conf = new Configuration();
        int exitCode = ToolRunner.run(conf, new PreprocessorDriver(), args);
        System.exit(exitCode);
    }
}
