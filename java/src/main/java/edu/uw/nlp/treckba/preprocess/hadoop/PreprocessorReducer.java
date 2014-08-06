package edu.uw.nlp.treckba.preprocess.hadoop;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

public class PreprocessorReducer extends MapReduceBase implements
		Reducer<Text, Text, Text, Text> {

	@Override
	public void reduce(final Text key, final Iterator<Text> values,
			final OutputCollector<Text, Text> output, final Reporter reporter)
			throws IOException {
		final Set<String> docs = new HashSet<String>();
		while (values.hasNext()) {
			docs.add(values.next().toString());
		}
		output.collect(key, new Text(Arrays.toString(docs.toArray())));
	}
}
