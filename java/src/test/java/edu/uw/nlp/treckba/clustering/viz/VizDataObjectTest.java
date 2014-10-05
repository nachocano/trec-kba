package edu.uw.nlp.treckba.clustering.viz;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.junit.Test;

import edu.uw.nlp.treckba.clustering.Cluster;

public class VizDataObjectTest {

	@Test
	public void testSerialize() {
		final Map<String, List<VizDataObject>> objects = new HashMap<String, List<VizDataObject>>();
		final List<VizDataObject> list = new LinkedList<>();
		final VizDataObject obj1 = new VizDataObject("streamid1", 1L,
				new float[] { 1, 2, 3 }, -1);
		final Cluster c = new Cluster(1, 1L, 86);
		final float[] ex = new float[300];
		ex[0] = 0.3f;
		ex[20] = 0.4f;
		ex[100] = 0.7f;
		ex[12] = 0.8f;
		c.updateSum(ex);
		c.incrementCount();
		obj1.setClusterName(c.getName());
		list.add(obj1);
		objects.put("entity", list);
		final ObjectMapper mapper = new ObjectMapper();
		try {
			mapper.writeValue(new File("test.json"), obj1);
		} catch (final JsonGenerationException e) {
			System.out.println("jsonGeneration Exception " + e.getMessage());
		} catch (final JsonMappingException e) {
			System.out.println("jsonMapping Exception " + e.getMessage());
		} catch (final IOException e) {
			System.out.println("io Exception " + e.getMessage());
		}
	}

}
