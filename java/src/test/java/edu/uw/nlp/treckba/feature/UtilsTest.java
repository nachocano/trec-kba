package edu.uw.nlp.treckba.feature;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.Assert;
import org.junit.Test;

import edu.uw.nlp.treckba.utils.Utils;

public class UtilsTest {

	@Test
	public void testGetMostFrequent() {
		final Map<ExampleKey, List<ExampleValue>> noisy = new HashMap<>();
		final List<ExampleValue> list1 = new ArrayList<>();
		list1.add(new ExampleValue(5, "date1"));
		list1.add(new ExampleValue(5, "date1"));
		list1.add(new ExampleValue(5, "date1"));
		final ExampleKey truthKey1 = new ExampleKey("streamid1", "targetId1");
		noisy.put(truthKey1, list1);

		final List<ExampleValue> list2 = new ArrayList<>();
		list2.add(new ExampleValue(2, "date2"));
		final ExampleKey truthKey2 = new ExampleKey("streamid2", "targetId2");
		noisy.put(truthKey2, list2);

		final List<ExampleValue> list3 = new ArrayList<>();
		list3.add(new ExampleValue(1, "date3"));
		list3.add(new ExampleValue(2, "date3"));
		list3.add(new ExampleValue(4, "date3"));
		final ExampleKey truthKey3 = new ExampleKey("streamid3", "targetId3");
		noisy.put(truthKey3, list3);

		final Map<ExampleKey, ExampleValue> actual = Utils.getMostFrequent(noisy);

		Assert.assertEquals(Integer.valueOf(5), actual.get(truthKey1)
				.getRelevance());
		Assert.assertEquals(Integer.valueOf(2), actual.get(truthKey2)
				.getRelevance());
		Assert.assertEquals(Integer.valueOf(4), actual.get(truthKey3)
				.getRelevance());

		Assert.assertEquals("date1", actual.get(truthKey1).getDateHour());
		Assert.assertEquals("date2", actual.get(truthKey2).getDateHour());
		Assert.assertEquals("date3", actual.get(truthKey3).getDateHour());

	}
}
