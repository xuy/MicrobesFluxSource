/* 
 * Copyright (c) 2011, Eric Xu (xuy@google.com)
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are met:
 *
 *  Redistributions of source code must retain the above copyright notice, 
 *  this list of conditions and the following disclaimer.
 *  Redistributions in binary form must reproduce the above copyright notice, 
 *  this list of conditions and the following disclaimer in the documentation 
 *  and/or other materials provided with the distribution.
 *  
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
 *  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
 *  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
 *  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
 *  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
 *  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
 *  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
 *  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
 *  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
 *  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
 *  POSSIBILITY OF SUCH DAMAGE.
 */

package edu.wustl.keggproject.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */

public class MicrobesFlux implements EntryPoint {
    public void onModuleLoad() {
        RootPanel rootPanel = RootPanel.get();
        rootPanel.setWidth("100%");

        Image logoImage = new Image();
        logoImage.setUrl("media/logo.png");
        LoginPanel loginpanel = new LoginPanel();

        LeftPanel leftp = new LeftPanel();
        VerticalPanel rightVerticalPanel = new VerticalPanel();// rightVerticalPanel=sfp+rightp+amp;

        RightPanel rightp = new RightPanel();
        StatusFormPanel sfp = new StatusFormPanel();

        rightp.initialize();
        sfp.initialize();

        leftp.setRightPanel(rightp);
        leftp.setStatusFormPanel(sfp);

        rightp.setStatusFormPanel(sfp);
        loginpanel.setRightPanel(rightp);

        rightVerticalPanel.add(sfp.getStatusFormPanel());
        rightVerticalPanel.add(rightp.getRightPanel());


        HorizontalPanel lower = new HorizontalPanel(); // lower=leftp+rightVerticalPanel;
        lower.add(leftp.getLeftPanel());
        lower.add(rightVerticalPanel);

        VerticalPanel fullpanel = new VerticalPanel(); // fullpanel==rootpanel; fullpanel=loginpanel+lower;
        fullpanel.add(logoImage);
        fullpanel.add(loginpanel.getLoginPanel());
        fullpanel.add(lower);
        rootPanel.add(fullpanel, 0, 0);

		/*
        DockLayoutPanel p = new DockLayoutPanel(Style.Unit.CM);
		p.setSize("100%", "900px");
		p.addNorth(logoPane, 1000);
		p.addWest(leftp.getLeftPanel(), 1000);
		p.addEast(rightVerticalPanel, 1000);
		rootPanel.add(p);
		*/
    }
}