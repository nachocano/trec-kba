package edu.uw.nlp.treckba.plot

import java.io.File

import org.apache.commons.cli._
import org.apache.commons.lang.Validate
import org.sameersingh.scalaplot.{XYChart, Style}
import org.sameersingh.scalaplot.gnuplot.GnuplotPlotter
import org.sameersingh.scalaplot.metrics.PrecRecallCurve

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

object PrecisionRecall {

  def main(args: Array[String]) {

    val options = new Options()
    options.addOption("i", true, "input dir")
    options.addOption("o", true, "output directory")
    options.addOption("f", true, "output filename")

    val parser = new BasicParser()

    var inputDir: String = null
    var outputDir: String = null
    var outFilename: String = null
    try {
      val line = parser.parse(options, args)
      inputDir = line.getOptionValue("i")
      Validate.notNull(inputDir)
      outputDir = line.getOptionValue("o")
      Validate.notNull(outputDir)
      outFilename = line.getOptionValue("f")
      Validate.notNull(outFilename)

    } catch {
      case ex: Exception => {
        val formatter = new HelpFormatter()
        formatter.printHelp("precisionrecall", options)
        return
      }
    }



    val names = new ArrayBuffer[String]()
    val lists : ArrayBuffer[ArrayBuffer[(Double, Boolean)]] = new ArrayBuffer[ArrayBuffer[(Double, Boolean)]]
    val inputFiles = new File(inputDir).listFiles()
    for (file <- inputFiles) {
      if (!file.isDirectory()) {
        names += file.getName().replace("_", " ")
        val list = new ArrayBuffer[(Double, Boolean)]
        for (line <- Source.fromFile(file).getLines) {
          val values = line.split(" ")
          val prob = values(0).toDouble
          var truth = false
          if (values(1).toInt == 1)
            truth = true
          val tuple = (prob, truth)
          list += tuple
        }
        lists += list
      }
    }

    val length = lists.length
    val curve = new PrecRecallCurve(lists(0))
    val chart = curve.prChart(names(0))

   for (index <- 1 to length-1) {
      val anotherCurve = new PrecRecallCurve(lists(index))
      val anotherChart = anotherCurve.prChart(names(index))
      chart.data += anotherChart.data.serieses.head
    }

    chart.data.serieses.foreach(_.pointType= Some(Style.PointType.Dot))
    //chart.showLegend = true
    val c = new XYChart(None, chart.data, chart.x, chart.y)
    c.showLegend = true
    val plotter = new GnuplotPlotter(c)
    plotter.pdf(outputDir, outFilename)
  }
}
