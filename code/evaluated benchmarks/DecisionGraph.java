import gov.nasa.jpf.vm.Verify;

public class DecisionGraph {
	
	//Internal state
	private int previousMode; 
	private int previousOutputState; 
	private int previousOutput;
	
	//Outputs
	private int primaryOutput;
	private int secondaryOutput;
	private int systemMode;
	
	public DecisionGraph() {
		previousMode = 0;	
		previousOutputState = 0;
		previousOutput = 100;
		primaryOutput = 0;
		secondaryOutput = 0;
		systemMode = 0;
	}
	
	public void update(int inputLevel, boolean automaticMode, 
			boolean overrideEnabled) {
		int outputRegulatorState; 
		int intermediateBufferState; 
		int overrideCommand; 
		boolean isNormalState; 
		int userCommand; 
		int autoCommand; 
		boolean switchToAlternateMode; 
		int modeDelay; 
		int primaryOutputLevel; 
		int secondaryOutputLevel; 
		int outputDelay; 
		int primarySourceState; 
		int selectedOutput; 
		int bufferOutput; 
		int feedbackDelay; 
		
	   feedbackDelay = previousOutput; 
	   outputDelay = previousOutputState; 
	   modeDelay = previousMode; 

	   isNormalState = (modeDelay == 0); 

	   if ((inputLevel == 0)) {
		      userCommand = 0;
		   } else { 
			   if ((inputLevel == 1)) {
			      userCommand = 1;
			   }  else { 
				   if ((inputLevel == 2)) { 
				      userCommand = 2;
				   } else { 
					   if ((inputLevel == 3)) { 
					      userCommand = 3;
					   } else { 
						   if ((inputLevel == 4)) {
						      userCommand = 4;
						   }  else { 
						      userCommand = 0;
						   }
					   }
				   }
			   }
		   }
	   
	   if ((automaticMode && 
		         isNormalState)) {
		      autoCommand = 1; 
		   }  else { 
		      autoCommand = 0;
		   }
	   
	   switchToAlternateMode = ((((!(outputDelay == 0)) && 
	         (feedbackDelay <= 0)) && 
	         isNormalState) || 
	         (!isNormalState)); 

	   if (switchToAlternateMode) {
	      if (overrideEnabled) 
	         secondaryOutputLevel = 0; 
	      else 
	         secondaryOutputLevel = 4; 
	   }
	   else { 
	      secondaryOutputLevel = 4;
	    } 

	   if (switchToAlternateMode) {
	      primarySourceState = 0; 
	   }  else { 
	      primarySourceState = 5; 
	    } 

	   if ((primarySourceState >= 1)) { 
	      bufferOutput = 0; 
	   }
	   else { 
	      bufferOutput = 5; 
	   }

	   if ((!switchToAlternateMode)) {
	      intermediateBufferState = 0; 
	   }  else { 
		   if ((bufferOutput >= 1)) { 
		      intermediateBufferState = bufferOutput;
		   }
		   else { 
		      intermediateBufferState = 5;
		   }
	   }

	   if ((secondaryOutputLevel == 0)) {
	      outputRegulatorState = 0;
	   }  else { 
		   if ((secondaryOutputLevel == 1))  {
		      outputRegulatorState = (intermediateBufferState / 4);
		   }  else {  
			   if ((secondaryOutputLevel == 2))  {
			      outputRegulatorState = (intermediateBufferState / 2);
			   }  else { 
				   if ((secondaryOutputLevel == 3)) { 
				      outputRegulatorState = ((intermediateBufferState / 4) * 3);
				   }  else { 
					   if ((secondaryOutputLevel == 4)) { 
					      outputRegulatorState = intermediateBufferState;
					   }  else { 
					      outputRegulatorState = 0;
					   }
				   }
			   }
		   }
	   }	   

	   if (overrideEnabled) {
	      overrideCommand = 0;
	   }  else { 
	      overrideCommand = (autoCommand+userCommand);
	   }

	   if (switchToAlternateMode) {
	      systemMode = 1; 
	   }  else { 
	      systemMode = 0;
	   }

	   if (switchToAlternateMode) {
	      primaryOutputLevel = 0; 
	   }  else { 
		   if (((overrideCommand >= 0) && 
		         (overrideCommand < 1))) {					   
		      primaryOutputLevel = 0; 
		   } else { 
			   if (((overrideCommand >= 1) && 
			         (overrideCommand < 2)))  {
			      primaryOutputLevel = 1; 
			   }  else { 
				   if (((overrideCommand >= 2) && 
				         (overrideCommand < 3))) {
				      primaryOutputLevel = 2; 
				   } else { 
					   if (((overrideCommand >= 3) && 
					         (overrideCommand < 4)))  {
					      primaryOutputLevel = 3; 
					   } else { 
					      primaryOutputLevel = 4;
					   }
				   }
			   }
		   }
	   }

	   if ((primarySourceState >= 1))  {
	      selectedOutput = primarySourceState;
	   }  else { 
	      selectedOutput = 0;
	   }

	   if ((primaryOutputLevel == 0)) {
	      primaryOutput = 0; 
	   }  else { 
		   if ((primaryOutputLevel == 1)) {
		      primaryOutput = (selectedOutput / 4);
		   }  else {
			   if ((primaryOutputLevel == 2)) {
			      primaryOutput = (selectedOutput / 2);
			   }  else { 
				   if ((primaryOutputLevel == 3)) {
				      primaryOutput = ((selectedOutput / 4) * 3);
				   } else { 
					   if ((primaryOutputLevel == 4)) { 
					      primaryOutput = selectedOutput;
					   } else { 
					      primaryOutput = 0;
					   }
				   }
			   }
		   }
	   }

	   if ((userCommand == 0)) {
	      secondaryOutput = 0; 
	   }  else {
		   if ((userCommand == 1)) {
		      secondaryOutput = (outputRegulatorState / 4); 
		   }  else { 
			   if ((userCommand == 2)) {
			      secondaryOutput = (outputRegulatorState / 2);
			   } else { 
				   if ((userCommand == 3)) {
				      secondaryOutput = ((outputRegulatorState / 4) * 3);
				   } else { 
					   if ((userCommand == 4)) {
					      secondaryOutput = outputRegulatorState; 
					   } else { 
					      secondaryOutput = 0;
					   }
				   }
			   }
		   }
	   }

	   previousOutput = primaryOutput; 

	   previousOutputState = primaryOutputLevel; 

	   previousMode = systemMode; 

	}
	
	public static void launch(int inputLevel1, boolean automaticMode1, boolean overrideEnabled1, int inputLevel2, boolean automaticMode2, boolean overrideEnabled2, int inputLevel3, boolean automaticMode3, boolean overrideEnabled3) {
		DecisionGraph dg = new DecisionGraph();
		dg.update(inputLevel1, automaticMode1, overrideEnabled1);
		dg.update(inputLevel2, automaticMode2, overrideEnabled2);
		dg.update(inputLevel3, automaticMode3, overrideEnabled3);		
	}
	
	public static void main(String[] args) {
		launch(0,false,false,0,false,false,0,false,false);
	}
}
