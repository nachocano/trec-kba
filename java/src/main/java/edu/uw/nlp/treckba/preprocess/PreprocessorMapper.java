package edu.uw.nlp.treckba.preprocess;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;

import edu.uw.nlp.treckba.gen.ContentItem;

public class PreprocessorMapper extends MapReduceBase implements
		Mapper<Text, StreamItemWritable, Text, Text> {

	private final Set<String> targetEntities = new HashSet<String>();

	@Override
	public void configure(final JobConf conf) {
		super.configure(conf);
		try {
			addTargetEntities("entities");
		} catch (final IOException exc) {
			throw new RuntimeException(
					"Exception while getting entities files. Exc "
							+ exc.getMessage());
		}
	}

	private void addTargetEntities(final String filename) throws IOException {
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
		System.out.println("targetEntities "
				+ Arrays.toString(targetEntities.toArray()));
	}

	private final Text entity = new Text();

	@Override
	public void map(final Text key, final StreamItemWritable value,
			final OutputCollector<Text, Text> output, final Reporter reporter)
			throws IOException {
		if (value.isSetBody()) {
			final ContentItem content = value.getBody();
			if (content.isSetClean_visible()) {
				final String cleanVisible = content.getClean_visible()
						.toLowerCase();
				for (final String targetEntity : targetEntities) {
					if (cleanVisible.indexOf(targetEntity) != -1) {
						entity.set(targetEntity);
						output.collect(entity, key);
					}
				}
			}
		}
	}
}
